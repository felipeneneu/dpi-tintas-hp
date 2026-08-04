from models.database import Database


class PedidoModel:
    """Model para gerenciamento de pedidos."""

    def __init__(self):
        self.db = Database.get_instance()

    def criar(self, numero: str, nome: str = "") -> int:
        """Cria um novo pedido e retorna o id."""
        cursor = self.db.executar(
            "INSERT INTO pedidos (numero, nome) VALUES (?, ?)",
            (numero, nome),
        )
        self.db.commitar()
        return cursor.lastrowid

    def listar(self) -> list:
        """Retorna todos os pedidos."""
        return self.db.buscar_todos(
            "SELECT * FROM pedidos ORDER BY data_criacao DESC"
        )

    def buscar_por_id(self, pedido_id: int) -> dict | None:
        """Retorna um pedido pelo id."""
        return self.db.buscar_um(
            "SELECT * FROM pedidos WHERE id = ?", (pedido_id,)
        )

    def atualizar(self, pedido_id: int, numero: str, nome: str):
        """Atualiza dados de um pedido."""
        self.db.executar(
            "UPDATE pedidos SET numero = ?, nome = ? WHERE id = ?",
            (numero, nome, pedido_id),
        )
        self.db.commitar()

    def deletar(self, pedido_id: int):
        """Deleta um pedido."""
        self.db.executar("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
        self.db.commitar()

    def contar_impressoes(self, pedido_id: int) -> int:
        """Conta quantas impressoes estao associadas ao pedido."""
        resultado = self.db.buscar_um(
            "SELECT COUNT(*) as total FROM impressoes WHERE pedido_id = ?",
            (pedido_id,),
        )
        return resultado["total"] if resultado else 0
