# JSSCAN

JSSCAN是一款基于Jsfinder基础上二开工具用作快速在网站的js文件中提取URL的工具

提取URL的正则部分使用的是[LinkFinder](https://github.com/GerbenJavado/LinkFinder)



## 用法

**简单爬取**

```
python JSSCAN.py -u http://www.test.com
```

**完全爬取**

会爬取站点引用外部的URL和站点URL汇总在结果中输出

```
python JSSCAN.py -u http://www.test.com -all
```

**深入爬取**

深入爬取分为三档 分别为 -d 1  -d 2 -d 3 (d1 d2数量较大时 d3爬取会相对费时间 建议先d 1 d 2 判断网页URL情况) -all爬取网页引用的外部URL和站点URL

```
python JSSCAN.py -u http://www.test.com -d 1
```

```
python JSSCAN.py -u http://www.test.com -all -d 1
```

**文件输出**

-ou 自定义的xlsx文件名

```
python JSSCAN.py -u http://www.test.com -d 1 -ou test.xlsx
```



**截图**

```
python JSSCAN.py -u http://e.mi.com
```



<img src="C:\Users\x\AppData\Roaming\Typora\typora-user-images\image-20230929222816211.png" alt="image-20230929222816211" style="zoom: 50%;" />

```
python JSSCAN.py -u http://e.mi.com -all
```

-all 将此站点引用的URL也进行了输出 推荐先使用普通爬取 -u www.xxx.com -d 2 或者 -d 1  来进行网站URL初步探测 逐步深入判断效果最佳

<img src="C:\Users\x\AppData\Roaming\Typora\typora-user-images\image-20230929222842495.png" alt="image-20230929222842495" style="zoom: 50%;" />



如使用中存在BUG 或者有好的提议 欢迎各位师傅指点 V:MiNi_login

