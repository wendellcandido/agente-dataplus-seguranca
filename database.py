import psycopg2
from configs import Settings

settings = Settings()

def get_db_connection():
    """Estabelece conexão segura com o PostgreSQL"""
    try:
        conn = psycopg2.connect(settings.db_conn_str)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def registrar_auditoria(usuario_id: int, acao: str, detalhes: str, ip: str = "127.0.0.1"):
    """Registra logs de auditoria conforme a política de monitoramento"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tb_audit_logs (usuario_id, acao, detalhes, ip_origem) VALUES (%s, %s, %s, %s)",
                (usuario_id, acao, detalhes, ip)
            )
            conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Erro ao registrar auditoria: {e}")
        finally:
            conn.close()