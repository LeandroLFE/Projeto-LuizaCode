from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
        
app = FastAPI()
        
OK = "OK"
FALHA = "FALHA"    


class Endereco(BaseModel):
    '''
    Classe representando os dados do endereço do cliente
    '''
    rua: str
    cep: str
    cidade: str
    estado: str

    def __str__(self) -> str:
        return f"{self.rua} - {self.cep} - {self.cidade} - {self.estado}"


class Produto(BaseModel):
    '''
    Classe representando os dados do produto
    '''
    id: int
    nome: str
    descricao: str
    preco: float

    def __str__(self) -> str:
        return f"{self.id} - {self.nome} - {self.descricao} - {self.preco}"

class Produto_Carrinho(BaseModel):
    '''
    Classe representando os dados de um Produto dentro do Carrinho
    '''
    produto: Produto
    quantidade: int = 1
    sub_total: float = 0


class Carrinho_De_Compras(BaseModel):
    '''
    Classe representando o carrinho de compras de um cliente com uma lista de produtos    
    '''
    produtos: List[Produto_Carrinho] = []
    preco_total: float = 0
    quantidade_de_itens: int = 0


class Usuario(BaseModel):
    '''
    Classe representando os dados do cliente
    '''
    id: int
    nome: str
    email: str
    senha: str
    enderecos: List[Endereco] = []
    carrinho_compras: Carrinho_De_Compras = {}

# Inicialização dos bancos de dados     
db_usuarios = {}
db_produtos = {}


@app.post("/usuario/")
async def criar_usuário(usuario: Usuario)->str:
    '''
    POST novo usuario
    '''
    if usuario.id not in db_usuarios:
        db_usuarios[usuario.id] = usuario
        carrinho_compras = Carrinho_De_Compras(id_usuario=usuario.id)
        db_usuarios[usuario.id].carrinho_compras = carrinho_compras
        return OK, 'O usuário foi cadastrado no nosso banco de dados!'
    return FALHA
     
     
@app.get("/usuario/{id_usuario}/")
async def retornar_usuario(id_usuario: int):
    '''
    GET dados de um usuário por Id 
    '''
    if id_usuario in db_usuarios:
        return db_usuarios[id_usuario]
    return FALHA


@app.get("/usuario/nome/{nome}/")
async def retornar_usuario_com_nome(nome):
    '''
    GET dados de um usuário por nome
    '''
    primeiro_nome = nome.split()[0]
    lista_usuarios = []
    for id_usuario, dados_usuario in db_usuarios.items():
        if primeiro_nome in dados_usuario.nome:
            lista_usuarios.append(dados_usuario)
    return lista_usuarios


@app.delete("/usuario/{id_usuario}/")
async def deletar_usuario(id_usuario: int)->str:
    '''
    DELETE um usuário por id
    '''
    if id_usuario in db_usuarios:
        del db_usuarios[id_usuario]
        return "o usuário foi deletado do nosso banco de dados com sucesso"
    return FALHA
            

@app.get("/usuario/{id_usuario}/enderecos/")
async def retornar_enderecos_do_usuario(id_usuario: int)->str:
    '''
    GET os endereços de um usuário
    '''
    if id_usuario not in db_usuarios:
        return FALHA
    else:
        return db_usuarios[id_usuario].enderecos
           
@app.get("/emails/{dominio_requisitado}/")
async def retornar_emails_dominio(id_usuario: int, dominio_requisitado: str)->str:
    '''
    GET enderecos por dominio requisitado    
    '''
    if id_usuario not in db_usuarios:
        return FALHA
    lista_dominios = []
    for id_usuario, dados_usuario in db_usuarios:
        dominio = dados_usuario.email.split('@')[1]
        if dominio == dominio_requisitado:
            lista_dominios.append(dados_usuario.email)
    return lista_dominios

 
@app.post("/{id_usuario}/endereco/")
async def criar_endereco(id_usuario: int, novo_endereco: Endereco):
    '''
    POST novo endereços a um usuário
    '''
    if id_usuario not in db_usuarios:
        return FALHA
    for endereco in db_usuarios[id_usuario].enderecos:
        if endereco == novo_endereco:
            return FALHA
    db_usuarios[id_usuario].enderecos.append(novo_endereco)
    return OK


@app.delete("/{id_usuario}/endereco/")
async def deletar_endereco(id_usuario: int, endereco_a_deletar: Endereco):
    '''
    DELETE um endereco de um usuário
    '''
    if id_usuario not in db_usuarios:
        return FALHA
    if endereco_a_deletar not in db_usuarios[id_usuario].enderecos:
        return FALHA
    del db_usuarios[id_usuario].enderecos[endereco_a_deletar]
    return OK

@app.get("/produtos/")
async def get_produtos():
    '''
    GET DB_Produtos
    '''
    return db_produtos


@app.get("/produtos/{id_produto}/")
async def get_produtos_id(id_produto: int):
    '''
    GET um produto por Id
    '''
    if id_produto in db_produtos:
        return db_produtos[id_produto]
    return FALHA, "produto não encontrado"


@app.post("/produtos/")
async def criar_produtos(produtos: List[Produto])->List[Produto]:
    '''
    POST adiciona lista de produtos
    '''
    list_adicionados = []
    for produto in produtos:
        if produto.id not in db_produtos:
            db_produtos[produto.id] = produto
            list_adicionados.append(produto)
    return list_adicionados

@app.put("/produto/{id_produto}")
async def atualizar_produto(id_produto: int, produto_atualizado: Produto)->str:
    '''
    PUT atualiza um produto por Id
    '''
    if id_produto not in db_produtos:
        db_produtos[id_produto] = produto_atualizado
        return OK, 'O produto foi cadastrado no nosso banco de dados!'
    return FALHA

@app.delete("/produto/{id_produto}/")
async def deletar_produto(id_produto: int)->str:
    '''
    DELETE um produto por Id    
    '''
    if id_produto in db_produtos:
        del db_produtos[id_produto]
        return OK, 'produto deletado'
    return FALHA

async def atualiza_preco_total(id_usuario: int)->None:
    '''
    Método auxiliar para atualizar o preço total do carrinho
    '''
    db_usuarios[id_usuario].carrinho_compras.preco_total = sum([p.sub_total for p in db_usuarios[id_usuario].carrinho_compras.produtos])

@app.put("/carrinho/{id_usuario}/")
async def adicionar_produto_carrinho(id_usuario: int, produto: Produto)->str:
    if id_usuario not in db_usuarios:
        return FALHA, "usuário não encontrado"
    if produto.id not in db_produtos:
        return FALHA, "produto não encontrado"
    for produto_carrinho in db_usuarios[id_usuario].carrinho_compras.produtos:
        if produto_carrinho.produto.id == produto.id:
            produto_carrinho.quantidade += 1
            produto_carrinho.sub_total = produto_carrinho.produto.preco * produto_carrinho.quantidade
            await atualiza_preco_total(id_usuario)
            return OK, "atualizada quantidade"
    produto_carrinho = Produto_Carrinho(produto=produto, quantidade=1, sub_total=produto.preco)
    db_usuarios[id_usuario].carrinho_compras.produtos.append(produto_carrinho)
    db_usuarios[id_usuario].carrinho_compras.quantidade_de_itens += 1
    await atualiza_preco_total(id_usuario)
    return OK, "adicionado o produto ao carrinho"

@app.delete("/carrinho/{id_usuario}/{id_produto}/")
async def remover_produto_carrinho(id_usuario: int, id_produto: int)->str:
    if id_usuario not in db_usuarios:
        return FALHA, "usuário não encontrado"
    if id_produto not in db_produtos:
        return FALHA, "produto não encontrado"
    a_remover = None
    for produto_carrinho in db_usuarios[id_usuario].carrinho_compras.produtos:
        if produto_carrinho.produto.id == id_produto:
            produto_carrinho.quantidade -= 1
            produto_carrinho.sub_total = produto_carrinho.produto.preco * produto_carrinho.quantidade
            await atualiza_preco_total(id_usuario)
            if produto_carrinho.quantidade <=0:
                produto_carrinho.quantidade = 0
                a_remover = produto_carrinho
                break
            return OK, "atualizada quantidade"
    if a_remover is not None:
        db_usuarios[id_usuario].carrinho_compras.produtos.remove(a_remover)
        db_usuarios[id_usuario].carrinho_compras.quantidade_de_itens -= 1
        return OK, "removido o produto"
    return FALHA


@app.get("/carrinho/{id_usuario}/")
async def retornar_carrinho(id_usuario: int):
    if id_usuario not in db_usuarios:
        return FALHA
    if db_usuarios[id_usuario].carrinho_compras.produtos == []:
        return []
    return db_usuarios[id_usuario].carrinho_compras


@app.delete("/carrinho/{id_usuario}/")
async def deletar_carrinho(id_usuario: int):
    if id_usuario not in db_usuarios:
        return FALHA
    else:
        # del db_carrinhos[id_usuario]
        return OK
        
        
@app.get("/")
async def bem_vinda():
    return "Seja bem vinda"
    #buscar o carrinho e retornar ele ao inves de criar um novo.