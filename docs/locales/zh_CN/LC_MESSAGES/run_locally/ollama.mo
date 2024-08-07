��    
      l               �   J   �        6     
   F     Q    q  (   �    �  �   �  w  �  =        R  0   Y     �     �    �  9   �  -  
  �   8	   Next, we introduce more detailed usages of Ollama for running Qwen models. Ollama Once it is finished, you can run your ollama model by: Quickstart Run Ollama with Your GGUF Files Sometimes you don't want to pull models and you just want to use Ollama with your own GGUF files. Suppose you have a GGUF file of Qwen, ``qwen1_5-7b-chat-q4_0.gguf``. For the first step, you need to create a file called ``Modelfile``. The content of the file is shown below: Then create the ollama model by running: Visit the official website `Ollama <https://ollama.com/>`__ and click download to install Ollama on your device. You can also search models in the website, where you can find the Qwen1.5 models. Except for the default one, you can choose to run Qwen1.5-Chat models of different sizes by: `Ollama <https://ollama.com/>`__ helps you run LLMs locally with only a few commands. It is available at MacOS, Linux, and Windows. Now, Qwen1.5 is officially on Ollama, and you can run it with one command: Project-Id-Version: Qwen 
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2024-02-21 21:08+0800
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language: zh_CN
Language-Team: zh_CN <LL@li.org>
Plural-Forms: nplurals=1; plural=0;
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.14.0
 接着，我们介绍在Ollama使用Qwen模型的更多用法 Ollama 完成后，你即可运行你的ollama模型： 快速开始 在Ollama运行你的GGUF文件 有时您可能不想拉取模型，而是希望直接使用自己的GGUF文件来配合Ollama。假设您有一个名为 ``qwen1_5-7b-chat-q4_0.gguf`` 的Qwen的GGUF文件。在第一步中，您需要创建一个名为 ``Modelfile`` 的文件。该文件的内容如下所示： 然后通过运行下列命令来创建一个ollama模型 访问官方网站 `Ollama <https://ollama.com/>`__ ”，点击 ``Download`` 以在您的设备上安装Ollama。您还可以在网站上搜索模型，在这里您可以找到Qwen1.5系列模型。除了默认模型之外，您可以通过以下方式选择运行不同大小的Qwen1.5-Chat模型： `Ollama <https://ollama.com/>`__ 帮助您通过少量命令即可在本地运行LLM。它适用于MacOS、Linux和Windows操作系统。现在，Qwen1.5正式上线Ollama，您只需一条命令即可运行它： 