<<<<<<< HEAD
# pullama
A Pull Request summarizer powered by Ollama and Llama2
=======
# Pullama

Are you Tired of Pull Requests with empty descriptions? Or maybe there's a description, but it's thin, and you barely know where to begin?

Enters Pullama is an AI-backed tool that helps you and your team get more insightful descriptions about pull request changes and a suggested review path. Pullama will also optionally do a more extensive impact analysis, taking the whole codebase into account (rudimentary and slow at the moment).

## Installation

Pullama is not available in any package manager.

### Clone

```bash
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

### GitHub actions

```yaml
    - name: Checkout Pullama action
      uses: actions/checkout@v2
      with:
        repository: paulosuzart/pullama
    - name: Run pullama
      uses: ./pullama
      with:
        target: main
        impact_analysis: true
```

*IMPORTANT:* Pullama uses [FastEmbed](https://qdrant.github.io/fastembed/) and will download the embedding model during the pipeline execution. Add cache here so you save time and resources.

## How it works

Behind the scenes, Pullama leverages Langchain's [RetrievalQA](https://js.langchain.com/docs/modules/chains/popular/vector_db_qa) for the PR Diff analysis and [ConversationalRetrievalChain](https://js.langchain.com/docs/modules/chains/popular/chat_vector_db) for the whole code base analysis.

Pullama uses [Qdrant](https://qdrant.tech/) as an in-memory vector store to store the whole codebase after FastEmbed embeds it. FastEmbed makes it even faster to run end-to-end because it will not send your code to `llama2` but will embed locally.

The diff is inserted into the Vector store, and the file names and commit messages are passed directly via prompt.

### Impact Analysis
The PR changes might be small but still carry an impact risk. The initial idea of impact analysis is to see how the changes impact the whole codebase. But the understanding of the meaning of the code faces significant challenges:

1. Codebase size. Some repositories may contain thousands of files, and going through a Tex Split process takes ages.
2. The Loader is a simple loader unaware of the codebase language. Langchain has support for languages other than Java, though.
3. An actual language server and not a simple text similarity search might be more suitable during repo impact analysis.
>>>>>>> b26cf5b (first commit)
