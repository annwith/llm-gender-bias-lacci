# Imports
import logging
from logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

import hydra
import asyncio
import itertools
import pandas as pd
from omegaconf import DictConfig
from src.main.utils import expandir_templates, carregar_cache, expandir_templates_v2, gerar_chave_cache, salvar_cache, atualizar_cache_e_salvar_se_necessario, chamar_api_provider


INTERVALO_SALVAMENTO = 5


async def obter_resposta_modelo(cfg, contador, cache_respostas, system_prompt, prompt, abordagem, modelo, temperatura, repeticao, tentativa=1, max_tentativas=3):
    """Obtém resposta do modelo com sistema de cache e retry.
    
    Args:
        cfg: Configuração Hydra
        contador: Contador de novas respostas (passado por referência via lista)
        cache_respostas: Dicionário de cache
        system_prompt: Prompt do sistema
        prompt: Prompt do usuário
        abordagem: Provider da API (gemini, gpt, etc)
        modelo: Nome do modelo
        temperatura: Temperatura para geração
        repeticao: Número da repetição
        tentativa: Tentativa atual (para retry)
        max_tentativas: Número máximo de tentativas
        
    Returns:
        String com a resposta do modelo ou mensagem de erro
    """
    chave_cache = gerar_chave_cache(modelo, system_prompt, prompt, temperatura, repeticao)
    
    if chave_cache in cache_respostas:
        return cache_respostas[chave_cache]

    try:
        response = await chamar_api_provider(abordagem, modelo, temperatura, system_prompt, prompt)
        resposta_limpa = response.strip().rstrip('.').strip('"') if response else None

        if resposta_limpa:
            contador[0] = atualizar_cache_e_salvar_se_necessario(contador[0], chave_cache, resposta_limpa, cache_respostas, cfg.ARQUIVO_CACHE, INTERVALO_SALVAMENTO, logger)
            logger.info(f"✓ [{modelo}] Temp={temperatura} Rep={repeticao} → {resposta_limpa[:50]}...")
            return resposta_limpa
        else:
            logger.warning(f"Resposta vazia ou inválida (tentativa {tentativa}/{max_tentativas}) de {modelo}")
            
            if tentativa < max_tentativas:
                logger.info(f"Fazendo retry {tentativa + 1}/{max_tentativas}...")
                await asyncio.sleep(0.5)
                return await obter_resposta_modelo(cfg, contador, cache_respostas, system_prompt, prompt, abordagem, modelo, temperatura, repeticao, tentativa + 1, max_tentativas)
            else:
                logger.error(f"Máximo de tentativas ({max_tentativas}) atingido para resposta inválida")
                contador[0] = atualizar_cache_e_salvar_se_necessario(contador[0], chave_cache, "resposta_invalida", cache_respostas, cfg.ARQUIVO_CACHE, INTERVALO_SALVAMENTO, logger) 
                return "resposta_invalida"

    except Exception as e:
        logger.error(f"Erro ao consultar o modelo {modelo} (tentativa {tentativa}/{max_tentativas}): {e}")
        
        if tentativa < max_tentativas:
            logger.info(f"Fazendo retry {tentativa + 1}/{max_tentativas} após erro...")
            await asyncio.sleep(1.0)  # Espera um pouco mais em caso de erro
            return await obter_resposta_modelo(cfg, contador, cache_respostas, system_prompt, prompt, abordagem, modelo, temperatura, repeticao, tentativa + 1, max_tentativas)
        else:
            logger.error(f"Máximo de tentativas ({max_tentativas}) atingido. Retornando erro_api")
            contador[0] = atualizar_cache_e_salvar_se_necessario(contador[0], chave_cache, "erro_api", cache_respostas, cfg.ARQUIVO_CACHE, INTERVALO_SALVAMENTO, logger) 
            return "erro_api"

async def run(cfg):
    """Função principal que executa a coleta de respostas dos modelos."""
    tarefas = []
    resultados = []
    contador = [0]  # Usar lista para permitir modificação dentro de funções async
    
    # Expandir templates de system e user prompts
    system_expandidos = expandir_templates_v2(
        cfg.SYSTEM_PROMPT,
        cfg.CHAVES_SYSTEM_PROMPT
    )
    prompt_expandidos = expandir_templates_v2(
        cfg.PROMPTS,
        cfg.CHAVES_PROMPT
    )

    # print(f"System Prompts:", system_expandidos)
    # print(f"Prompts:", prompt_expandidos)
    # return None

    cache_respostas = carregar_cache(cfg.ARQUIVO_CACHE, logger)
    logger.info(f"Cache carregado com {len(cache_respostas)} respostas")

    # Criar todas as combinações de tarefas
    num_repeticoes = cfg.get('REPETICOES_POR_TEMP', 1)
    max_concorrencia = cfg.get('MAX_CONCORRENCIA', 10)
    semaphore = asyncio.Semaphore(max_concorrencia)
    
    async def tarefa_com_semaforo(system, prompt, modelo, temperatura, repeticao):
        """Wrapper que controla concorrência."""
        async with semaphore:
            model_name, provider = modelo
            resposta = await obter_resposta_modelo(
                cfg, contador, cache_respostas, 
                system["texto"], prompt["texto"], 
                provider, model_name, temperatura, repeticao
            )
            return {
                "modelo": model_name, 
                "temperatura": temperatura, 
                "repeticao": repeticao,
                "system_prompt": system["chaves_usadas"], 
                "user_prompt": prompt["chaves_usadas"],
                "resposta_raw": resposta
            }
    
    for (system, prompt, modelo, temperatura, repeticao) in itertools.product(
        system_expandidos, prompt_expandidos, cfg.MODELOS_A_AVALIAR, cfg.TEMPERATURES, range(1, num_repeticoes + 1)):
        
        tarefa = tarefa_com_semaforo(system, prompt, modelo, temperatura, repeticao)
        tarefas.append(tarefa)

    logger.info(f"Total de {len(tarefas)} tarefas criadas (max {max_concorrencia} simultâneas)")
    
    # Executar com controle de concorrência e tratamento de erros
    resultados = await asyncio.gather(*tarefas, return_exceptions=True)
    
    # Filtrar erros e contar sucessos
    resultados_validos = []
    erros = 0
    for i, resultado in enumerate(resultados):
        if isinstance(resultado, Exception):
            logger.error(f"Tarefa {i} falhou: {resultado}")
            erros += 1
        else:
            resultados_validos.append(resultado)
    
    logger.info(f"Respostas obtidas: {len(resultados_validos)} (erros: {erros})")

    # Criar DataFrame diretamente dos resultados
    df_resultados = pd.DataFrame(resultados_validos)

    # Salvar cache e resultados
    salvar_cache(cache_respostas, cfg.ARQUIVO_CACHE, logger)
    logger.info("Coleta de dados concluída!")
    
    df_resultados.to_csv(cfg.ARQUIVO_SAIDA, index=False)
    logger.info(f"Resultados salvos em {cfg.ARQUIVO_SAIDA}")
    
    arquivo_json = cfg.ARQUIVO_SAIDA.replace('.csv', '.jsonl')
    df_resultados.to_json(arquivo_json, orient='records', lines=True, force_ascii=False)
    logger.info(f"Resultados salvos em {arquivo_json}")
    
@hydra.main(version_base=None, config_path="conf", config_name="main_config")
def main(cfg : DictConfig) -> None:
    asyncio.run(run(cfg))

if __name__ == "__main__":
    main()