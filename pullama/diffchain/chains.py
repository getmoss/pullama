from langchain.vectorstores.qdrant import Qdrant
from langchain.llms import Ollama
from langchain.schema import Document
from langchain.chains import RetrievalQA
from git import Repo
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dataclasses import dataclass
from langchain_core.embeddings import Embeddings
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import Language
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

def lang_to_ext(language: Language) -> str:
    if Language.JAVA == language:
        return '.java'
    elif Language.PYTHON == language:
        return '.py'
    elif Language.GO == language:
        return '.go'
    else:
        print('{} is not supported'.format(language))
        exit(1)


@dataclass
class PullamaOptions:
    repo: str
    git_repo: Repo
    source: str
    target: str
    verbose: bool
    lang: Language


class DiffChain:
    def __init__(self, options: PullamaOptions):
        self.table = None
        self.repo = options.repo
        self.git_repo = options.git_repo
        self.source = options.source
        self.target = options.target
        self.verbose = options.verbose
        self.lang = options.lang

    def __diff_messages(self):
        messages = self.git_repo.git.log(
            "--pretty=%B", "{}...{}".format(self.source, self.target)
        )
        if self.verbose:
            print("commit messages")
            print(messages)
        return messages

    def __diff_text(self):
        diff = self.git_repo.git.diff(self.source, self.target)
        if self.verbose:
            print("diff content: ")
            print(diff)
        return diff

    def __diff_files(self):
        files = self.git_repo.git.diff("--name-only", self.source, self.target)
        if not files:
            return []
        else:
            return [f for f in files.split("\n")]

    def __prepare_store(self, embeddings: Embeddings):
        diff = self.__diff_text()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500, chunk_overlap=100
        )
        all_splits = [
            Document(page_content=x, metadata={"source": self.source})
            for x in text_splitter.split_text(diff)
        ]

        vectorstore = Qdrant.from_documents(
            all_splits,
            embedding=embeddings,
            location=":memory:",
            collection_name="my_dcs",
        )

        return vectorstore

    def check_impact(self, summary, embeddings: Embeddings, llm: Ollama) -> str:
        from .prompts import impact_prompt

        data = DirectoryLoader(
            self.repo,
            show_progress=True,
            glob="**/*.{}".format(lang_to_ext(self.lang)),
            loader_cls=TextLoader,
            randomize_sample=True,
            sample_size=600,
        ).load()
        code_splitter = RecursiveCharacterTextSplitter.from_language(
            language=self.lang, chunk_size=1000, chunk_overlap=200
        )
        texts = code_splitter.split_documents(data)
        vectorstore = Qdrant.from_documents(
            texts, embedding=embeddings, location=":memory:", collection_name="my_dcs"
        )

        memory = ConversationBufferMemory(
            llm=llm, memory_key="chat_history", return_messages=True
        )
        memory.save_context(
            {"input" :"Summarize these changes in a diff: " + self.__diff_text() },
            {"output": summary}
        )

        qa = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            memory=memory,
            verbose=self.verbose,
        )
        analysis_result = qa(
            {
                "question": impact_prompt
            }
        )

        return analysis_result["answer"]

    def summarize(self, embeddings: Embeddings, llm: Ollama) -> str:
        from .prompts import summary_prompt
        store = self.__prepare_store(embeddings)
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            verbose=self.verbose,
            retriever=store.as_retriever(search_kwargs={'score_threshold': 0.8}),
        )

        final_prompt = summary_prompt.format(
            files=", ".join(self.__diff_files()), messages=self.__diff_messages()
        )
        if self.verbose:
            print(final_prompt)
        response = qa_chain({"query": final_prompt})
        return response["result"]
