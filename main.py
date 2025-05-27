import streamlit as st
from azure.storage.blob import BlobServiceClient
import pymssql
import uuid
import os

# Configurações do Azure SQL Database
SQL_SERVER = "bookecommerceserver.database.windows.net"
SQL_DATABASE = "VendaDB"
SQL_USER = "adminuser"
SQL_PASSWORD = "P@ssw0rd123!"

# Configurações do Azure Blob Storage
STORAGE_CONNECTION_STRING = "SUA_CONNECTION_STRING_AQUI"  # Substitua pela Connection String do Azure Storage
CONTAINER_NAME = "product-images"

# Inicializar cliente do Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Conexão com o banco de dados
def get_db_connection():
    return pymssql.connect(
        server=SQL_SERVER,
        user=SQL_USER,
        password=SQL_PASSWORD,
        database=SQL_DATABASE
    )

# Função para upload de imagem para o Blob Storage
def upload_image(file):
    blob_name = f"{uuid.uuid4()}_{file.name}"
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file, overwrite=True)
    return blob_client.url

# Função para criar um produto
def create_product(nome, descricao, preco, imagem_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Produtos (nome, descricao, preco, imagem_url)
        VALUES (%s, %s, %s, %s)
        """,
        (nome, descricao, preco, imagem_url)
    )
    conn.commit()
    cursor.close()
    conn.close()

# Função para listar todos os produtos
def read_products():
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute("SELECT * FROM Produtos")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

# Função para atualizar um produto
def update_product(id, nome, descricao, preco, imagem_url=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if imagem_url:
        cursor.execute(
            """
            UPDATE Produtos
            SET nome=%s, descricao=%s, preco=%s, imagem_url=%s
            WHERE id=%s
            """,
            (nome, descricao, preco, imagem_url, id)
        )
    else:
        cursor.execute(
            """
            UPDATE Produtos
            SET nome=%s, descricao=%s, preco=%s
            WHERE id=%s
            """,
            (nome, descricao, preco, id)
        )
    conn.commit()
    cursor.close()
    conn.close()

# Função para deletar um produto
def delete_product(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Produtos WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

# Interface Streamlit com Bootstrap
st.set_page_config(page_title="E-Commerce", layout="wide")

# Incluir Bootstrap via CDN
st.markdown(
    """
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <style>
        .main-container { max-width: 1200px; margin: auto; padding: 20px; }
        .product-card { height: 100%; }
        .product-img { height: 200px; object-fit: cover; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 class="text-center mb-4">E-Commerce</h1>', unsafe_allow_html=True)

# Abas para navegação
tab1, tab2 = st.tabs(["Adicionar/Editar Produto", "Listar Produtos"])

# Aba para criar/editar produtos
with tab1:
    st.markdown('<h3 class="mb-4">Adicionar ou Editar Produto</h3>', unsafe_allow_html=True)
    edit_id = st.selectbox("Selecionar Produto para Editar", ["Novo Produto"] + [f"{p['id']}: {p['nome']}" for p in read_products()])
    edit_id = int(edit_id.split(":")[0]) if edit_id != "Novo Produto" else None

    with st.form("product_form", clear_on_submit=True):
        nome = st.text_input("Nome do Livro", value="" if not edit_id else next(p['nome'] for p in read_products() if p['id'] == edit_id))
        descricao = st.text_area("Descrição", value="" if not edit_id else next(p['descricao'] for p in read_products() if p['id'] == edit_id))
        preco = st.number_input("Preço (R$)", min_value=0.0, step=0.01, value=0.0 if not edit_id else next(p['preco'] for p in read_products() if p['id'] == edit_id))
        imagem = st.file_uploader("Imagem do Produto", type=["jpg", "png"], accept_multiple_files=False)
        submit_button = st.form_submit_button("Salvar")

        if submit_button:
            if nome and preco > 0:
                imagem_url = upload_image(imagem) if imagem else (next(p['imagem_url'] for p in read_products() if p['id'] == edit_id) if edit_id else None)
                if edit_id:
                    update_product(edit_id, nome, descricao, preco, imagem_url)
                    st.success("Produto atualizado com sucesso!")
                else:
                    create_product(nome, descricao, preco, imagem_url)
                    st.success("Produto adicionado com sucesso!")
            else:
                st.error("Preencha o nome e o preço do produto.")

# Aba para listar produtos
with tab2:
    st.markdown('<h3 class="mb-4">Lista de Produtos</h3>', unsafe_allow_html=True)
    products = read_products()
    if products:
        cols = st.columns(3)
        for idx, product in enumerate(products):
            with cols[idx % 3]:
                st.markdown(
                    f"""
                    <div class="card product-card mb-4">
                        <img src="{product['imagem_url']}" class="card-img-top product-img" alt="{product['nome']}">
                        <div class="card-body">
                            <h5 class="card-title">{product['nome']}</h5>
                            <p class="card-text">{product['descricao'][:100]}...</p>
                            <p class="card-text"><strong>R$ {product['preco']:.2f}</strong></p>
                            <button class="btn btn-danger" onclick="deleteProduct({product['id']})">Deletar</button>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        st.markdown(
            """
            <script>
            function deleteProduct(id) {
                if (confirm('Tem certeza que deseja deletar este produto?')) {
                    fetch('/delete_product', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                        body: 'id=' + id
                    }).then(response => window.location.reload());
                }
            }
            </script>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("Nenhum produto cadastrado.")

# Endpoint para deletar produto (simulado via Streamlit)
if st._is_running_with_streamlit:
    @st.experimental_memo
    def delete_endpoint():
        if "id" in st.experimental_get_query_params():
            delete_product(int(st.experimental_get_query_params()["id"][0]))
    delete_endpoint()
