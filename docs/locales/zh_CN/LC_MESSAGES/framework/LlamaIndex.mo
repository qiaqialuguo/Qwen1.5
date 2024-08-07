��          �               �      �   
   	  2     c   G     �     �     �  �   �  d   l  >   �  �     Q     C   ]  w  �  �    
   �  3   �  S        q     ~     �  �   �  K   *	  '   v	    �	  f   �
  K      Build Index LlamaIndex Now we can build index from documents or websites. Now you can perform queries, and Qwen1.5 will answer based on the content of the indexed documents. Preparation RAG Set Parameters The following code snippet demonstrates how to build an index for files (regardless of whether they are in PDF or TXT format) in a local folder named 'document'. The following code snippet demonstrates how to build an index for the content in a list of websites. The following is a simple code snippet showing how to do this: To connect Qwen1.5. with external data, such as documents, web pages, etc., we offer a tutorial on `LlamaIndex <https://www.llamaindex.ai/>`__. This guide helps you quickly implement retrieval-augmented generation (RAG) using LlamaIndex with Qwen1.5. To implement RAG, we advise you to install the LlamaIndex-related packages first. To save and load the index, you can use the following code snippet. Project-Id-Version: Qwen 
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2024-03-18 18:47+0800
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language: zh_CN
Language-Team: zh_CN <LL@li.org>
Plural-Forms: nplurals=1; plural=0;
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.14.0
 现在，我们可以设置语言模型和向量模型。Qwen1.5-Chat支持包括英语和中文在内的多种语言对话。您可以使用``bge-base-en-v1.5``模型来检索英文文档，下载``bge-base-zh-v1.5``模型以检索中文文档。根据您的计算资源，您还可以选择``bge-large``或``bge-small``作为向量模型，或调整上下文窗口大小或文本块大小。Qwen 1.5模型系列支持最大32K上下文窗口大小。 LlamaIndex 现在我们可以从文档或网站构建索引。 现在您可以输入查询，Qwen1.5 将基于索引文档的内容提供答案。 环境准备 检索增强（RAG） 设置参数 以下代码片段展示了如何为本地名为'document'的文件夹中的文件（无论是PDF格式还是TXT格式）构建索引。 以下代码片段展示了如何为一系列网站的内容构建索引。 以下是一个简单的代码示例： 为了实现 Qwen1.5 与外部数据（例如文档、网页等）的连接，我们提供了 `LlamaIndex <https://www.llamaindex.ai/>`__ 的详细教程。本指南旨在帮助用户利用 LlamaIndex 与 Qwen1.5 快速部署检索增强生成（RAG）技术。 为实现检索增强生成（RAG），我们建议您首先安装与 LlamaIndex 相关的软件包。 要保存和加载已构建的索引，您可以使用以下代码示例。 