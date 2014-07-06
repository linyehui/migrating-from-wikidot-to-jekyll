把Blog数据从Wikidot迁移到Jekyll
================================
migrating-from-wikidot-to-jekyll

# 目标
> 把Wikidot的Blog数据迁移到Jekyll

### 目标分解：
* Blog原文从之前的Wiki格式转换成Markdown
* 保持原有的文章发布时间，标题，文章的Url，tag信息

**PS.**
为什么把博客从Wikidot迁移出来？
为什么选择Github Pages + Jekyll 而不是Farbox或者其他？
这个先沉淀下，同时也用段时间验证下，过段时间再和大家分享。

# 问题分析
## 基本情况介绍
* Wikidot支持Backup，但是备份出来的数据压缩包解压出来就是些纯文本，文件名是url名字，文件内容就是Wiki格式的文章内容，没有文章发布的时间，没有tag信息；
* 想拿到全的RSS，但试了半天RSS还是只导出了22篇文章，不知道怎么拿到老的数据RSS。

## 尝试 1：能不能直接使用 Jekyll-import
* 我也想用，但是没找到直接对Wikidot的支持，对Wiki格式的支持也没有；
* 如果想从RSS导入的话，Wikidot导出的RSS又不全
* 无奈放弃

## 尝试 2：能不能曲线救国，先转成Wordpress再转
看了下，有位哥们脚本实现了：[wikidot-to-markdown](https://github.com/vLj2/wikidot-to-markdown)，但是他只是对格式的转换，这个代码我可以复用，但是……

#### 但是来了：
* 前提是我得先有数据给他转换，从上面介绍Wikidot直接提供给我们的数据是不够的
* 我的目的是放到Jekyll上，也就是说我的文件头需要加上Jakyll的配置，这个我还得另外写个脚本来做
* 需求描述变成了：
    ```
    1. 从Wikidot拿到所有文章的索引信息（Title，Url，tags，Date），和backup中的文件关联起来；
    2. 再处理下backup中的文件，加上文件头，把正文从Wiki转成Mardown
    ```
到此，问题分析的七七八八了，结论是我要写个脚本来做这个事情。

# 解决方案
## 拿到WIkidot所有文章的索引
没能拿到全的RSS，但是全的索引还是可以拿到的，但是需要再wikidot下页面单独来做这个事情，比如我的：
> http://www.linyehui.com/misc:rss

这个Wikidot页面的源码如下：
```
[[module ListPages category="_default" perPage="500" date="@URL" separate="false" prependLine="||~ Page||~ Date created||~ Tags ||"]]
|| %%linked_title%% || %%date%% || %%tags%% ||
[[/module]]
```

## 从Wikidot后台Backup并下载Zip包
解压后的文件路径类似：
> ~/backup_linyehui_20140705_1759UTC/source/system_recent-changes.txt

## 写脚本
有了上面两步，我就能拿到全索引，并用索引把backup目录下的文件关联起来了
对脚本感兴趣的可以直接看代码：
> https://github.com/linyehui/migrating-from-wikidot-to-jekyll

### 这里说下脚本的使用方式：
1. git clone 得到两个脚本文件 
> git clone https://github.com/linyehui/migrating-from-wikidot-to-jekyll
2. 从Wikidot 管理后台备份Blog，并下载下来，解压后得到source目录，放到脚本下的wikidot根目录（是的，我的脚本不对文件进行处理）
3. 新建一个Wikidot页面，用于生成所有文章的RSS（我这文章数上限设置的是500，你可以自己调整），生成的RSS保存成rss.html，把文件复制到脚本下的wikidot根目录

    我新建了这个页面：
    > http://www.linyehui.com/misc:rss
    
    页面代码如下（点击Edit就能编辑）：
    ```
    [[module ListPages category="_default" perPage="500" date="@URL" separate="false" prependLine="||~ Page||~ Date created||~ Tags ||"]]
    || %%linked_title%% || %%date%% || %%tags%% ||
    [[/module]]
    ```
4. 现在的脚本目录结构如下：
    ```
    |----wikidot
    |    |-convert.py
    |    |-wikidot.py
    |    |-rss.html
    |    |-source
    |        |- xxxx-xxx1.txt
    |        |- xxxx-xxx2.txt
    ```
5. 执行convert.py，不带参数会使用默认的目录结构进行执行，执行后你就能再脚本旁边的./jekyll目录下得到你所需要的转换后的.markdown文件们
6. 把.markdown文件全选，复制到github pages对应git目录下的_post目录，git commit，git push
7. 迁移工作搞定。