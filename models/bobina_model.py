from models.database import Database


class BobinaModel:
    """Model para gerenciamento de bobinas."""

    def __init__(self):
        self.db = Database.get_instance()

    def criar(self, tamanho: str, material: str, tipo: str) -> int:
        """Cria uma nova bobina e retorna o id."""
        cursor = self.db.executar(
            "INSERT INTO bobinas (tamanho, material, tipo) VALUES (?, ?, ?)",
            (tamanho, material, tipo),
        )
        self.db.commitar()
        return cursor.lastrowid

    def listar(self) -> list:
        """Retorna todas as bobinas."""
        return self.db.buscar_todos("SELECT * FROM bobinas ORDER BY id DESC")

    def buscar_por_id(self, bobina_id: int) -> dict | None:
        """Retorna uma bobina pelo id."""
        return self.db.buscar_um(
            "SELECT * FROM bobinas WHERE id = ?", (bobina_id,)
        )

    def atualizar(self, bobina_id: int, tamanho: str, material: str, tipo: str):
        """Atualiza dados de uma bobina."""
        self.db.executar(
            "UPDATE bobinas SET tamanho = ?, material = ?, tipo = ? WHERE id = ?",
            (tamanho, material, tipo, bobina_id),
        )
        self.db.commitar()

    def deletar(self, bobina_id: int):
        """Deleta uma bobina."""
        self.db.executar("DELETE FROM bobinas WHERE id = ?", (bobina_id,))
        self.db.commitar()

    def contar_impressoes(self, bobina_id: int) -> int:
        """Conta quantas impressoes estao associadas a bobina."""
        resultado = self.db.buscar_um(
            "SELECT COUNT(*) as total FROM impressoes WHERE bobina_id = ?",
            (bobina_id,),
        )
        return resultado["total"] if resultado else 0
