from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import threading

from experiments import RaspilumController


raspilum = None

# Impede dois experimentos de controlarem a máquina simultaneamente
experiment_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):

    global raspilum

    print("================================")
    print("Inicializando backend Raspilum")
    print("================================")

    raspilum = RaspilumController()

    yield

    print("================================")
    print("Finalizando backend Raspilum")
    print("================================")


app = FastAPI(
    title="Raspilum API",
    description="API para controle dos experimentos da Raspilum",
    version="1.0.0",
    lifespan=lifespan
)


def executar_experimento(funcao):

    if not experiment_lock.acquire(blocking=False):

        raise HTTPException(
            status_code=409,
            detail="A Raspilum está executando outro experimento."
        )

    try:

        funcao()

        return {
            "status": "concluido",
            "message": "Experimento executado com sucesso."
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Erro durante o experimento: {str(e)}"
        )

    finally:

        experiment_lock.release()


@app.get("/")
def root():

    return {
        "status": "online",
        "sistema": "Raspilum",
        "message": "Backend funcionando."
    }


@app.get("/status")
def status():

    return {
        "status": "online",
        "raspilum_inicializada": raspilum is not None,
        "experimento_em_execucao": experiment_lock.locked()
    }


@app.post("/experimentos/fenolftaleina")
def executar_fenolftaleina():

    return executar_experimento(
        raspilum.experimento_fenolftaleina
    )


@app.post("/experimentos/azul-de-metileno")
def executar_azul_de_metileno():

    return executar_experimento(
        raspilum.experimento_azul_de_metileno
    )


@app.post("/experimentos/cloreto")
def executar_cloreto():

    return executar_experimento(
        raspilum.experimento_cloreto
    )