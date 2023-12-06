from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.stdout import StdOutCallbackHandler
from langchain.llms import Ollama
from langchain.embeddings import FastEmbedEmbeddings
from git import Repo
from langchain.text_splitter import Language
import click

from diffchain import DiffChain, PullamaOptions


@click.command()
@click.option("--server", help="Ollama Server", default='http://localhost:11434')
@click.option("--repo", "-r", help="Repo to summarize.")
@click.option("--source", "-s", prompt="Source branch", help="Source branch/commit for the diff.")
@click.option("--target", "-t", default="master", help="The target branch/commit for the diff.")
@click.option("--language", "-l", default="JAVA", help="Main language of the repo. JAVA, PYTHON, GO supported.")
@click.option(
    "--assess",
    "-a",
    default=False,
    is_flag=True,
    help="Enable impact asessment against codebase (rudimentary)",
)
@click.option(
    "--verbose", "-v", is_flag=True, default=False, help="User verbose for models"
)
def pullama(server, repo, source, target, assess, verbose: bool, language: str):
    git_repo = Repo(repo)
    for remote in git_repo.remotes:
        remote.fetch()
    opts = PullamaOptions(repo, git_repo, source, target, verbose, lang=Language[language])
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-base-en")

    llm = Ollama(
        base_url=server,
        model="llama2",
        verbose=verbose,
        callback_manager=CallbackManager([StdOutCallbackHandler()]),
    )

    diffchain = DiffChain(opts)
    summary = diffchain.summarize(embeddings, llm)
    print(summary)
    if assess:
        impact = diffchain.check_impact(summary, embeddings, llm)
        print(impact)

