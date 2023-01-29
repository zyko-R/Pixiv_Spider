# Pixiv_Spider
## 功能
1. 根据画师信息, 将该作者的艺术作品集下载到本地  
2. 根据画作信息, 将相似艺术作品集下载到本地  
3. 将每日排行榜上的艺术作品下载到本地  
4. 将关注画师们的艺术作品集下载到本地

## 使用说明
### 运行 Main 方法以启动
- 下载艺术作品以登陆为前提，首次使用时会要求输入账号&密码，直到正确为止
  - 以后登陆皆会调用文件里的账号密码，不会要求用户重新输入
  - 登陆信息有效期间不会进行模拟登陆，不必担心频繁登陆的问题
![image.png](https://s2.loli.net/2023/01/07/k3KtSz1pENdDsBh.png)
  - 其余操作根据终端提示操作即可, 运行完毕后目录下会自动生成含艺术作品集的文件夹
## 目录与文件说明
- ### Downloader
>Lib.Requester实现网络请求  
PluginsXProxy实现其附加功能和接口
- ### PixivCrawler.Crawler
>Plugins 实现捕获艺术作品ID的方案  
Prototype.IDHandler 通过访问Prototype.Lib内的组件以处理ID
- ### PixivCrawler.CrawlerCaller
>*组合IDHandler和Plugin为系列指令，并提供执行接口*
- ### Client
>*调用CrawlerCaller并提供菜单*

## Pixiv_Spider的工作原理
### 准备工作:
#### 模拟登陆  
- 使用Selenium模块打开浏览器 访问`https://accounts.pixiv.net/login?return_to=https://www.pixiv.net`
- 通过xpath表达式 `//*[@class="sc-bn9ph6-1 hJBrSP"]/input[@autocomplete="username"]` 找到输入账号的位置并输入
- 通过xpath表达式 `//*[@class="sc-bn9ph6-1 hJBrSP"]/input[@autocomplete="current-password"]` 找到输入密码的位置并输入
- 通过xpath表达式 `//button[@type="submit"]`找到登陆按钮并点击
***
### 次要信息收集：
#### 获取画师名字
- 访问 `https://www.pixiv.net/users/{author_id}` 获取html文件
- 使用xpath表达式 `//head/title/text()` + 正则表达式 `(.*?) - pixiv` 获取
#### 获取画师ID
- 访问`https://www.pixiv.net/search_user.php?nick={author_name}&s_mode=s_usr`
- 使用xpath表达式`//h1/a[@target="_blank"][@class="title"]/@href`+ 正则表达式`\w+/(\d+)`获取
***
### 主要捕获艺术作品ID的方式:
#### 根据画师ID获取艺术作品ID
- 访问`https://www.pixiv.net/ajax/user/{author_id}/profile/all?lang=zh` 获取json文件 
- 通过正则表达式`\d+`解析 捕获全部艺术作品ID
#### 根据画作ID获取相似艺术作品ID
- 访问`https://www.pixiv.net/ajax/illust/{param}/recommend/init?limit={source_limit}&lang=zh`  获取json文件 
- 遍历`['body']['illusts']`中的`['id']`捕获全部艺术作品ID
#### 根据每日排行榜获取艺术作品ID
- 访问`https://www.pixiv.net/ranking.php?mode=daily(_18)` 获取html文件
- 通过正则表达式`"data-type=".*?"data-id="(.*?)"`解析 捕获全部艺术作品ID
#### 根据"关注画师最新作品"获取艺术作品ID
- 访问`https://www.pixiv.net/ajax/follow_latest/illust?p={page}&mode=all&lang=z` 获取json文件 
- `['body']['page']['ids']`捕获全部艺术作品ID
***
### 艺术作品ID的处理:
#### 分类
- 访问`https://www.pixiv.net/artworks/{artwork_id}` 获取html文件 
- 使用xpath表达式`//head/title/text()`/`//head/meta[@property="twitter:title"]/@content`解析 以R18-GIF分类ID
#### 处理img: 
- 访问 `https://www.pixiv.net/ajax/illust/{_id}/pages?lang=zh` 获取json文件
- 使用正则表达式`https://i\.pximg\.net/img-original/img/.*?_p\d+\..{3}`解析画作原地址 下载保存
#### 处理gif:
- 访问`https://www.pixiv.net/ajax/illust/{_id}/ugoira_meta?lang=zh` 获取到含，含所有图片的zip地址的html文件
- 通过代码`["body"]["originalSrc"]` 得到zip文件原地址
- 通过代码 `semi_delay = [item["delay"] for item in url_data["body"]["frames"]]`
  `delay = sum(semi_delay) / len(semi_delay) / 1000` 得到图片间隔时间
- 下载并解压zip文件，保存进文件夹，使用imageio读取，拼接成gif文件保存
## 版本更新:
- 2023-1-8 迁移了Login类和Request文件, 添加了菜单 + 小小的优化
- 2023-1-8 修复订阅系统的bug，添加了下载每日排行榜(normal+r18)的功能
- 2023-1-8 添加了本地追踪名单同步pixiv关注名单和下载关注画师们最新艺术作品集的功能
- 2023-1-9 将大部分解析方法更替成生成器 提升可读性 重写了菜单
- 2023-1-10 重写了插件 原型 组合之间的关系 结构性更强
- 2023-1-10 添加了下载相似艺术作品的功能
- 2023-1-11 统一了ArtworkIDMixin的接口 使实现更加直观 更改了目录结构
- 2023-1-14 多线程
- 2023-1-15
   - Process: 策略模式变更为策略模式+外观模式
   - 插件+原型变更为装饰器模式+适配器模式
- 2023-1-20: 大幅重写
   - HandleCell: 外观模式变更为模版方法模式
   - Requester: 空变更为装饰器模式+代理模式 
   - CrawlPlanner: 工厂方法模式变更为生成器模式+命令模式
   - 重写菜单 添加指令集和延迟执行功能
- 2023-1-26
   - HandleCell: 模版方法模式变更为桥接模式
   - HandleCell/Filter: 模版方法模式变更为过滤器模式
   - CrawlPlanner: 生成器模式融合命令模式变更为命令模式
   - 重写IDHandler执行逻辑和播报内容
   - 扩大错误处理范围
- 2023-1-29: 大幅重写
   - HandleCell改名Lib: 桥接模式->策略模式
   - Lib.HandleAPI: (全重写)集合处理变更为多个子处理并行
   - 增加进度条
