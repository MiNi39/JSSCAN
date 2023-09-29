# JSSCAN

JSSCAN是一款基于Jsfinder基础上二开工具用作快速在网站的js文件中提取URL的工具

提取URL的正则部分使用的是[LinkFinder](https://github.com/GerbenJavado/LinkFinder)



## 用法

**简单爬取**

```
python JSSCAN.py -u http://www.test.com
```

**完全爬取**

会爬取站点引用外部的URL和站点URL 汇总在结果中输出

```
python JSSCAN.py -u http://www.test.com -all
```

**深入爬取**

深入爬取分为三档 分别为 -d 1  -d 2 -d 3 (d1 d2数量较大时 d3爬取会相对费时间 建议先d 1 d 2 判断网页URL情况) -all爬取网页应用的外部URL以及本站

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
python JSSCAN.py -u http://e.mi.com -d 2
```

![image](https://github.com/MiNi39/JSSCAN/blob/main/img/1.jpg)

结果

![image](https://github.com/MiNi39/JSSCAN/blob/main/img/2.jpg)

```
python JSSCAN.py -u http://e.mi.com -d 2 -all
```

-all 将此站点引用的URL也进行了输出 推荐先使用普通爬取 -u www.xxx.com -d 2 或者 -d 1  来进行网站URL初步探测 逐步深入判断效果最佳

![image](https://github.com/MiNi39/JSSCAN/blob/main/img/3.jpg)

结果

![image](https://github.com/MiNi39/JSSCAN/blob/main/img/4.jpg)



