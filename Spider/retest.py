#!python
#-*- encoding: utf-8 -*-

'''
A script to test RE for unicode (GBK)
'''

import re


gbkstring = '''
 <h3>拍拍贷统计信息</h3>
                        <p>历史统计</p>
                        <p>正常还清：62 次，逾期还清(1-15)：0 次，逾期还清(>15)：0 次 </p>
                        <p>
                            共计借入：<span class="orange">&#165;354,929</span>，
                            待还金额：<span class="orange">&#165;207,453.96</span>，
                            待收金额： <span class="orange">
&#165;357,804.52                            </span>
                        </p>
'''

pattern = re.compile('<h3>拍拍贷统计信息</h3>.*?<p>历史统计</p>.*?<p>正常还清：(\d+).*?次，逾期还清\(1-15\)：(\d+).*?次，逾期还清\(>15\)：(\d+).*次 </p>' +
                      '.*?共计借入：<span class="orange">&#165;(\S+)</span>.*?待还金额：<span class="orange">&#165;(\S+)</span>' + 
                     '.*?待收金额： <span class="orange">.*?&#165;(\S+).*?</span>.*?</p>', re.S)

items = re.findall(pattern, gbkstring)
if items != None and len(items) > 0:
    print items
else:
    print "No Match!"

gbkstring2 = '''
   <div class="lendDetailTab w1000center">
        <div class="lendDetailTab_tabContent">
                                                    <!--魔镜-->
                    <h3>魔镜等级</h3>
                    <div class="waprMJ clearfix" style="position: relative;">
                        <div id="polar" style="height: 310px; width: 500px; float: left;"></div>
                        <div class="waprMjInfo" style="float: left; width: 300px; margin-left: 40px;">
                            <h3>什么是魔镜等级？</h3>
                            <p style="text-align: left;">
                                魔镜是拍拍贷自主开发的风险评估系统，
                                其核心是一系列基于大数据的风险模型。<br />
                                针对每一笔借款，风险模型会给出一个风险评分，以反应对其逾期率的预测。<br />
                                每一个评分区间会以一个字母评级的形式展示给借入者和借出者。从A到F，风险依次上升。<br />
                                <a href="http://help.ppdai.com/Home/List/12" target="_blank">了解更多</a>
                            </p>
                            <strong class="levelMJ" title="魔镜等级：AAA至F等级依次降低，等级越高逾期率越低。点击等级了解更多。">C</strong>
                        </div>
                    </div>
                <!--魔镜结束-->

                    <h3>借款人相关信息</h3>
                    <p>基本信息：以下信息由借入者提供，拍拍贷未核实。如果您发现信息不实，请点此举报。拍拍贷核实后如果发现严重不符合事实，将扣信用分甚至取消借款资格。</p>
                    <table class="lendDetailTab_tabContent_table1">
                        <tr>
                            <th>借款目的</th>
                            <th>性别</th>
                            <th>年龄</th>
                            <th>婚姻情况</th>
                            <th>文化程度</th>
                            <th>住宅状况</th>
                            <th>是否购车</th>
                        </tr>
                        <tr>

                            <td>其他</td>

                            <td>男</td>
                            <td>36</td>

                            <td>已婚</td>

                            <td>大专</td>

                            <td>
有房                            </td>

                            <td>是</td>
                        </tr>
                    </table>
'''
pattern_user_basic_info = re.compile('<div class="lendDetailTab w1000center">.*?<div class="lendDetailTab_tabContent">.*?' 
                                    + '<table class="lendDetailTab_tabContent_table1">.*?<tr>.*?</tr>.*?<tr>.*?' 
                                    + '<td>(\S*?)</td>.*?<td>(\S+)</td>.*?<td>(\S+?)</td>.*?<td>(\S+?)</td>.*?' 
                                    + '<td>(.*?)</td>.*?<td>.*?(\S+).*?</td>.*?<td>(.*?)</td>.*?</tr>.*?</table>', re.S)

items = re.findall(pattern_user_basic_info, gbkstring2)
if items is not None:
    for item in items:
        print item[0]

url = 'http://invest.ppdai.com/loan/info?id=8314822'
loanid = re.match('.*info\?id=(\d+)', url)
if loanid is not None:
    print loanid.group(1)