from langchain.prompts import PromptTemplate

summary_prompt = PromptTemplate.from_template(
    """
====
The changed files in this diff: {files}. Concentrate your analysis on these files only.
To help you understand the changes, here are the commit messages: {messages} (do not use them as the sole criteria)
====
Given you are preparing a pull request for your colleagues, summarize the git diff and out in markdown format:

Add a Summary for summarize the change in at most one paragraph.
Add a Additions section for laying down the code additions in terms of meaning. Be more detailed here.
Add a Updates section tohighlight the code updates in terms of meaning. Be more detailed here.
Add a Deletes section to tell removed code, if any.
Add a Review order section. In this section suggest a good order to check files so a reviewer can easily follow the changes. Here indicate the files and the source.

Important: Never output again the whole or part of the diff. You don't need to reproduce each change, \
just highlight the change and how the code looks like after the change. Feel free to rise a potential business impact with the change. 
Remember java classes end in .java, groovy classes in .groovy and kotlin in .kt. Also remember that diff files use a plus sign to indicate additions and negative sign to indicate removals. It is not useful to know a new line was added, changed or removed. We are here for the meaning of things. Also do not sensitive data if you see them.
"""
)

impact_prompt = "Thanks for summarizing the changes. Tell me how this summarized changes (without making suppositions) can affect my whole codebase. Please mention the source of places that can be impacted by the changes above and the expected outcome of the changes. Do not make comments about the existing codebase, but rather on the changes applied to it. Do not make generic engineering suggestions of improvements. If impact is not clear, don't bring generic comments."