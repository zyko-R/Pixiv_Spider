# Pixiv_Spider
## 功能
- ### 聚焦
输入pixiv作者的名字或ID, 将指定数量的艺术作品下载到本地  
将每日排行榜上的艺术作品下载到本地  
将关注画师们的艺术作品集下载到本地  

  
- ### 增量
通过作者ID/同步pixiv->订阅作者, 动态更新本地的艺术作品
## 运行Pixiv_Spider需要的依赖
   - python 3.11
   - [ lxml , selenium, aiohttp, aiofiles, re, asyncio, nest_asyncio, imageio, zipfile ]
      ### 运行 Main 方法以启动
## 简简单单的使用说明
- 下载艺术作品以登陆为前提，首次使用时会要求输入账号&密码，直到正确为止
  - 以后登陆皆会调用文件里的账号密码，不会要求用户重新输入
  - 登陆信息有效期间不会进行模拟登陆，不必担心频繁登陆的问题!
![image.png](https://s2.loli.net/2023/01/07/k3KtSz1pENdDsBh.png)
  - 其余根据终端提示操作即可, 运行完毕后目录下会自动生成艺术作品集的zip文件
## 目录与文件说明
- ### src / IDProcess
*存放了获取到artwork_id后的通用处理组件* 
- Parser组件活动于网络 负责解析网络请求和发起网络请求
- Pipline组件活动于本地 负责处理最终数据
- ### src / Spider
*存放了自定义爬虫的各种组件*
- Plugins(插件)制定了各种获取ID的方法
- Prototype(原型)将IDProcess封装成一个通用爬虫
- Factory(工厂)将原型与插件组合成特殊行为的爬虫
## To-do List:
- [x] ***特定画师全画作下载***
- [x] ***模拟登陆***
- [x] ***关注画师(同步pixiv/手动追加)->本地艺术作品更新***  
- [x] ***每日排行榜艺术作品下载***
- [ ] ***特定标签画作下载***
- [ ] ***热门艺术作品下载***
- [ ] ***完美的自定义接口与内部结构。。。***
## Pixiv_Spider的工作原理
### 准备工作:
#### 模拟登陆  
- 使用Selenium模块打开浏览器 访问`https://accounts.pixiv.net/login?return_to=https://www.pixiv.net`
- 通过xpath表达式 `//*[@class="sc-bn9ph6-1 hJBrSP"]/input[@autocomplete="username"]` 找到输入账号的位置并输入
- 通过xpath表达式 `//*[@class="sc-bn9ph6-1 hJBrSP"]/input[@autocomplete="current-password"]` 找到输入密码的位置并输入
- 通过xpath表达式 `//button[@type="submit"]`找到登陆按钮并点击
- 反复直到成功将cookie保存于文件 并移交给aiohttp.ClientSession()
***
### 次要信息收集：
#### 获取画师名字
- 通过aiohttp异步访问 `https://www.pixiv.net/users/{author_id}` 获取含画师名字的html文件
- 使用xpath表达式 `//head/title/text()` + 正则表达式 `(.*?) - pixiv`
- 得到画师名字 为文件夹命名
#### 获取画师ID
- 通过aiohttp异步访问`https://www.pixiv.net/search_user.php?nick={author_name}&s_mode=s_usr`
- 使用xpath表达式`//h1/a[@target="_blank"][@class="title"]/@href`+ 正则表达式`\w+/(\d+)`得到画师id
#### 根据用户ID同步追踪名单
- 通过aiohttp异步访问`https://www.pixiv.net/ajax/user/{user_id}/following?` 得到含有关注画师ID的json文件
- 通过代码`for user in json['body']['users']: write_in(user['userId'])`将关注画师ID及其最新作品ID记录入文件，以便后续更新
***
### 主要捕获艺术作品ID的方式:
#### 根据特定画师ID获取艺术作品ID
- 通过aiohttp异步访问`https://www.pixiv.net/ajax/user/{author_id}/profile/all?lang=zh` 获取到含全部艺术作品ID的json文件 
- 通过正则表达式`\d+`获取到全部艺术作品ID
#### 根据每日排行榜获取艺术作品ID
- 通过aiohttp异步访问`https://www.pixiv.net/ranking.php?mode=daily(_18)` 获取到含画作ID的html文件
- 通过正则表达式`"data-type=".*?"data-id="(.*?)"`获取到全部艺术作品ID
#### 根据"关注画师最新作品"获取艺术作品ID
- 通过aiohttp异步访问`https://www.pixiv.net/ajax/follow_latest/illust?p={page}&mode=all&lang=z` 获取到含全部艺术作品ID的json文件 
- 通过代码`id_list += [0]['body']['page']['ids']`获取到全部艺术作品ID
***
### 艺术作品ID的处理:
#### 分类
- 通过aiohttp异步访问`https://www.pixiv.net/artworks/{artwork_id}` 获取到含艺术作品tag`gif, r18`的html文件 
- 使用xpath表达式`//head/title/text()`+`//head/meta[@property="twitter:title"]/@content`得到tag，进行ID分类
#### 处理img: 
- 访问 `https://www.pixiv.net/ajax/illust/{_id}/pages?lang=zh` 获取含艺术作品资源地址的json文件
- 使用正则表达式`https://i\.pximg\.net/img-original/img/.*?_p\d+\..{3}`解析画作原地址
- 下载二进制文件，通过aiofiles异步保存图片
#### 处理gif:
- 访问`https://www.pixiv.net/ajax/illust/{_id}/ugoira_meta?lang=zh` 获取到含每帧间隔时间，含所有图片的zip地址的html文件
- 通过代码`["body"]["originalSrc"]`访问json, 得到zip文件原地址
- 下载并解压zip文件，保存进文件夹，使用imageio读取，拼接成gif文件保存
#### 收尾
- 使用zipfile压缩r18, normal文件夹
## 版本更新:
- 2023-1-8 迁移了Login类和Request文件, 添加了菜单 + 小小的优化
- 2023-1-8 修复订阅系统的bug，添加了下载每日排行榜(normal+r18)的功能
- 2023-1-8 添加了本地追踪名单同步pixiv关注名单+下载关注画师们最新艺术的功能
- 2023-1-9 将大部分解析方法更替成生成器 提升可读性 重写了菜单
- 2023-1-10 重写了插件 原型 组合之间的关系 结构性更强