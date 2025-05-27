# dio-azure-cloud-native-lab01
Desafio Microsoft Azure Cloud Native - Armazenando dados de um E-Commerce na Cloud

## Pré-requisitos

- Conta ativa no [Microsoft Azure](https://portal.azure.com) com acesso ao plano gratuito.
- [Python 3.8+](https://www.python.org/downloads/) instalado localmente.
- [Git](https://git-scm.com/) instalado para gerenciar o repositório.
- Editor de código como [VS Code](https://code.visualstudio.com/).
- Conta no [GitHub](https://github.com/) com um repositório criado para este projeto.

## Passo a Passo para Configuração

### 1. Criar um Resource Group no Azure

1. Acesse o [Portal do Azure](https://portal.azure.com) e faça login.
2. No menu lateral, clique em **Resource Groups** > **Criar**.
3. Insira:
   - **Nome do Resource Group**: `BookEcommerceRG`
   - **Assinatura**: Selecione sua assinatura gratuita.
   - **Região**: Escolha uma região próxima, como `East US`.
4. Clique em **Revisar + Criar** e, em seguida, **Criar**.

### 2. Criar um Azure SQL Database

1. No Portal do Azure, clique em **Criar um recurso** > **SQL Database**.
2. Configure:
   - **Assinatura**: Sua assinatura gratuita.
   - **Resource Group**: `BookEcommerceRG`.
   - **Nome do Banco de Dados**: `VendaDB`.
   - **Servidor**: Crie um novo servidor com:
     - **Nome do Servidor**: `bookecommerceserver` (único globalmente).
     - **Localização**: Mesma região do Resource Group (`East US`).
     - **Autenticação**: Use autenticação SQL com:
       - **Usuário**: `adminuser`
       - **Senha**: `P@ssw0rd123!` (anote, será usada no `main.py`).
   - **Nível de Serviço**: Selecione **Basic** (plano gratuito, 5 DTUs, 2 GB).
3. Clique em **Revisar + Criar** e, em seguida, **Criar**.
4. Após a criação, vá para o servidor SQL criado, em **Configurações** > **Regras de Firewall**, e adicione uma regra para permitir o acesso do seu IP local (selecione **Adicionar IP do cliente**).

### 3. Criar a Tabela de Produtos no Banco de Dados

1. No Portal do Azure, vá para o banco de dados `VendaDB` > **Editor de Consultas**.
2. Faça login com as credenciais do servidor (`adminuser`, `P@ssw0rd123!`).
3. Execute o seguinte comando SQL para criar a tabela `Produtos`:

```sql
CREATE TABLE Produtos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(255),
    descricao VARCHAR(MAX),
    preco DECIMAL(18,2),
    imagem_url NVARCHAR(2083)
)
```

4. Clique em **Executar** e verifique se a tabela foi criada com sucesso.

### 4. Criar uma Conta de Armazenamento (Storage Account)

1. No Portal do Azure, clique em **Criar um recurso** > **Conta de Armazenamento**.
2. Configure:
   - **Assinatura**: Sua assinatura gratuita.
   - **Resource Group**: `BookEcommerceRG`.
   - **Nome da Conta**: `bookecommercestorage` (deve ser único globalmente).
   - **Localização**: `East US`.
   - **Desempenho**: **Standard**.
   - **Redundância**: **LRS** (Locally-redundant storage, mais econômico).
3. Clique em **Revisar + Criar** e, em seguida, **Criar**.
4. Após a criação, vá para a conta de armazenamento criada > **Contêineres** > **+ Contêiner**.
5. Crie um contêiner chamado `product-images` com nível de acesso **Blob** (acesso anônimo para leitura).

### 5. Obter Credenciais do Azure Storage

1. No Portal do Azure, vá para a conta de armazenamento `bookecommercestorage` > **Chaves de Acesso**.
2. Copie a **Connection String** da **Chave 1** (será usada no `main.py`).

### 6. Configurar o Projeto Localmente

1. Clone o repositório GitHub para sua máquina local:
   ```bash
   git clone <URL_DO_SEU_REPOSITORIO>
   cd <NOME_DO_REPOSITORIO>
   ```
2. Crie um ambiente virtual Python:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate      # Windows
   ```
3. Instale as dependências listadas em `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

### 7. Implementar o Código no `main.py`

O arquivo `main.py` contém o código da aplicação, com:
- Conexão ao Azure SQL Database para gerenciar produtos.
- Integração com Azure Blob Storage para upload e exibição de imagens.
- Interface CRUD usando Streamlit com estilização Bootstrap.

Copie o conteúdo do arquivo `main.py` (disponível neste repositório) para sua máquina.

### 8. Configurar Credenciais no `main.py`

Edite o arquivo `main.py` e substitua as credenciais do Azure SQL Database e do Azure Storage pelas suas, obtidas nos passos 2 e 5. As credenciais estão hard-coded no arquivo, conforme solicitado.

### 9. Executar a Aplicação Localmente

1. Com o ambiente virtual ativado, execute:
   ```bash
   streamlit run main.py
   ```
2. Acesse a aplicação no navegador em `http://localhost:8501`.

### 10. Fazer o Deploy no GitHub

1. Adicione os arquivos ao repositório:
   ```bash
   git add .
   git commit -m "Adiciona e-commerce com Azure"
   git push origin main
   ```

## Estrutura do Projeto

- `main.py`: Código principal da aplicação com CRUD, integração com Azure Blob Storage e SQL Database.
- `requirements.txt`: Lista de dependências do projeto.
- `README.md`: Este arquivo com instruções detalhadas.

## Notas Adicionais

- O plano gratuito do Azure tem limitações (ex.: 5 DTUs no SQL Database, 20.000 RU/s no Blob Storage). Monitore o uso no Portal do Azure.
- Para segurança em produção, armazene credenciais em um arquivo `.env` ou use Azure Key Vault.
- Teste todas as funcionalidades CRUD (criar, listar, atualizar, deletar) na interface Streamlit.

## Resolução de Problemas

- **Erro de conexão com o SQL Database**: Verifique se o IP do cliente está na regra de firewall do servidor SQL.
- **Erro de upload de imagem**: Confirme que o contêiner `product-images` tem acesso anônimo configurado como **Blob**.
- **Erro de dependências**: Certifique-se de que o ambiente virtual está ativado e as dependências estão instaladas.

---

### Explicação dos Arquivos

1. **main.py**:
   - **Conexão com o Banco de Dados**: Usa `pymssql` para conectar ao Azure SQL Database com as credenciais hard-coded.
   - **Gerenciamento de Imagens**: Implementa o upload de imagens para o Azure Blob Storage e retorna a URL pública.
   - **CRUD**: Inclui funções para criar, ler, atualizar e deletar produtos, separadas por comentários claros.
   - **Interface Streamlit**: Usa Streamlit para criar uma interface com duas abas: uma para adicionar/editar produtos e outra para listar/deletar produtos.
   - **Bootstrap**: Integra Bootstrap via CDN para estilizar os cards de produtos e formulários.

2. **requirements.txt**:
   - Lista as dependências necessárias: `streamlit`, `azure-storage-blob` e `pymssql`.

### Notas
- Substitua `SUA_CONNECTION_STRING_AQUI` no `main.py` pela string de conexão do Azure Storage obtida no passo 5 do `README.md`.
- Certifique-se de que o contêiner `product-images` no Azure Blob Storage está configurado com acesso anônimo de leitura para exibir as imagens corretamente.
- O plano gratuito do Azure tem limitações, como 2 GB de armazenamento no SQL Database e 20.000 RU/s no Blob Storage. Monitore o uso no Portal do Azure.


