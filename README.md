# Pullama

Are you Tired of Pull Requests with empty descriptions? Or maybe there's a description, but it's thin, and you barely know where to begin?

Say no more! `pullama` is an AI-backed tool that helps you and your team get more insightful descriptions about pull request changes and a suggested review path. Pullama will also optionally do a more extensive impact analysis, taking the whole codebase into account (rudimentary and slow at the moment).

When using the GitHub Action provided, pullama will analyze the PR changes, add a comment with the summary, and suggest a review path for the reviewers. A real example output:

```markdown
Summary: The pull request changes focus on updates to the .github directory, particularly in the test.yml and workflows/test.yml files. These updates include adding a forced server, changing the target branch, and updating the path for the "ollama" job. Additionally, there are changes in the README.md file, including adding an actual language server during impact analysis, and updates to the action.yml file to use the latest version of pipenv. Finally, there are updates to the pullama.py file, including changing the remote fetch behavior and adding FastEmbedEmbeddings for the model_name.

Additions:

* The addition of a forced server in the test.yml file
* The change in the target branch from ${{ github.base_ref }} to "master" in the test.yml file
* The update to the path for the "ollama" job in the workflows/test.yml file

Updates:

* The update to the README.md file to include an actual language server during impact analysis
* The update to the action.yml file to use the latest version of pipenv

Deletes:

* There are no deletions in this pull request

Review Order:

* Start by reviewing the files in the .github directory, specifically the test.yml and workflows/test.yml files, as they contain the majority of the changes.
* Next, review the README.md file for any updates or changes that may impact the overall project.
* Finally, review the pullama.py file to ensure there are no issues with the code additions or updates.

Potential Business Impact:

* The update to the target branch may impact the build process, as it may require additional configuration or testing to ensure proper functionality.
* The addition of an actual language server during impact analysis may improve the accuracy of the assessment, but may also introduce new dependencies or requirements that need to be considered.
```

## Installation and run

Pullama is available on [pypi](https://pypi.org/project/pullama/).

```shell
# Using a virtualenv recommended
pip install pullama
```

Then run pullama:

```shell
TOKENIZERS_PARALLELISM=true python -m pullama -r /paht/to/repo/terraform-provider-metabase \
-s 482a09ee4ca319a296a901bf6c88474b955eee5f \
-t 69e52645c1d7ccfe50d00aeb43f820a3896fd04b
```

### Clone

Clone from Moss's public repo [pullama](https://github.com/getmoss/pullama).

If you want to clone the project, install the dependencies with `pipenv`.

```bash
> python -m pullama --help

Usage: pullama.py [OPTIONS]

Options:
  --server TEXT        Ollama Server
  -r, --repo TEXT      Repo to summarize.
  -s, --source TEXT    Source branch/commit for the diff.
  -t, --target TEXT    The target branch/commit for the diff.
  -l, --language TEXT  Main language of the repo. JAVA, PYTHON, GO supported.
  -a, --assess         Enable impact asessment against codebase (rudimentary)
  -v, --verbose        User verbose for models
  --help               Show this message and exit.
```

The `repo` option is just the path to the local cloned repository. While `source` and `target` represent the commits (or branches) you are analyzing.


*IMPORTANT:* Pullama uses [FastEmbed](https://qdrant.github.io/fastembed/) and will download the embedding model during the pipeline execution. Add cache here so you save time and resources.

## Ollama

You also need Ollama reachable from your machine. You can run it locally like this:

```
docker run  -v ollama:/root/.ollama -p 11435:11434 --name ollama22 ollama/ollama
docker exec -it ollama ollama pull llama2
```

## How it works

Behind the scenes, Pullama leverages Langchain's [RetrievalQA](https://js.langchain.com/docs/modules/chains/popular/vector_db_qa) for the PR Diff analysis and [ConversationalRetrievalChain](https://js.langchain.com/docs/modules/chains/popular/chat_vector_db) for the whole code base analysis.

Pullama uses [Qdrant](https://qdrant.tech/) as an in-memory vector store to store the whole codebase after FastEmbed embeds it. FastEmbed makes it even faster to run end-to-end because it will not send your code to `llama2` but will embed locally.

The diff is inserted into the Vector store, and the file names and commit messages are passed directly via prompt.

### Impact Analysis
The PR changes might be small but still carry an impact risk. The initial idea of impact analysis is to see how the changes impact the whole codebase. But the understanding of the meaning of the code faces significant challenges:

1. Codebase size. Some repositories may contain thousands of files, and going through a Tex Split process takes ages.
2. The Loader is a simple loader unaware of the codebase language. Langchain has support for languages other than Java, though.
3. An actual language server and not a simple text similarity search might be more suitable during repo impact analysis.
