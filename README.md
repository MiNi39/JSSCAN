# JSSCAN

JSSCAN是一款基于Jsfnder基础上二开工具用作快速在网站的js文件中提取URL的工具

提取URL的正则部分使用的是[LinkFinder](https://github.com/GerbenJavado/LinkFinder)



## 用法

**简单爬取**

```
python JSSCAN1.0.py -u http://www.test.com
```



**深入爬取**

深入爬取分为三档 分别为 -d 1  -d 2 -d 3

推荐先使用d1 d2 来进行判断网站URL数量 若数量较大 d3会消耗更长

```
python JSSCAN1.0.py -u http://www.test.com -d 1
```



**文件输出**

-ou 自定义的xlsx文件名

```
python JSSCAN1.0.py -u http://www.test.com -d 1 -ou test.xlsx
```



**截图**

```
python JSSCAN1.0.py -u http://e.mi.com
```

![image-20230928112230288](C:\Users\x\AppData\Roaming\Typora\typora-user-images\image-20230928112230288.png)