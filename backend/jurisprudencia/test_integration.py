# Teste de integração real com a API DJEN
# Este arquivo deve ser executado manualmente para testar a API real

import os
import sys
import django

# Configurar Django
sys.path.append('/Users/fernandotorres/Juris-Dev-agil/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juris_ai.settings')
django.setup()

from jurisprudencia.utils.djen import DJENClient


def test_djen_real_api():
    """Teste de integração real com a API DJEN"""
    print("🧪 Testando integração real com API DJEN...")
    
    try:
        # Inicializar cliente
        client = DJENClient()
        print("✅ Cliente DJEN inicializado com sucesso")
        
        # Teste 1: Health Check
        print("\n📡 Testando health check...")
        health_result = client.health_check()
        print(f"Status: {health_result['status']}")
        print(f"Mensagem: {health_result['message']}")
        
        # Teste 2: Busca simples
        print("\n🔍 Testando busca simples...")
        search_result = client.buscar_julgados(
            termo="responsabilidade civil",
            pagina=1,
            itensPorPagina=5
        )
        
        print(f"Status da busca: {search_result.get('status', 'N/A')}")
        if 'items' in search_result:
            print(f"Quantidade de itens encontrados: {len(search_result['items'])}")
            if search_result['items']:
                print("Primeiro item:")
                first_item = search_result['items'][0]
                print(f"  - ID: {first_item.get('id', 'N/A')}")
                print(f"  - Título: {first_item.get('titulo', 'N/A')[:100]}...")
        else:
            print("Nenhum item encontrado ou erro na busca")
        
        # Teste 3: Busca com parâmetros específicos
        print("\n🎯 Testando busca com parâmetros específicos...")
        specific_search = client.buscar_julgados(
            termo="danos morais",
            dataInicio="2023-01-01",
            dataFim="2023-12-31",
            siglaTribunal="TJSP",
            pagina=1,
            itensPorPagina=3
        )
        
        print(f"Status da busca específica: {specific_search.get('status', 'N/A')}")
        if 'items' in specific_search:
            print(f"Quantidade de itens na busca específica: {len(specific_search['items'])}")
        
        print("\n✅ Teste de integração concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_djen_real_api()
