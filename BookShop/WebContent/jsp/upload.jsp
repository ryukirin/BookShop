<!-- <%@ page language="java" pageEncoding="utf-8"%> 
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<!doctype html>
<html>
<head>
    <title>我的作业</title>
<link rel="stylesheet" type="text/css" href="../css/changepwd.css"></link>
</head>
<body>
实现文件的上传 -->
<!-- 1.要上传文件 表单提交请求的方式必须为post请求 -->
<!-- 2.要上传文件 需要设置form表单的enctype
	application/x-www-form-urlencoded是form表单enctype的默认值
	需要将enctype的值设置为 multipart/form-data



<div class="header" id="head">
  <div class="title">你好！</div>
  <div class="tab">
		  <ul>
		  	<li>
		  		<a href="course.action?opttype=queryAllcourse">课程</a>
		  	</li>
		  	<li>
		  		<a href="blog.action?opttype=queryAllblog">博客</a>
		  	</li>
		  	<li class="selected">
		  		<a href="my.action?opttype=initMypage">个人</a>
		  	</li>
		  </ul>
	</div>
</div>
<div class="wrap" id="wrap">
	<div id="leftbar">
		<table class="lefttable">
			<tr>
				<th><a href="chagepwd.jsp">修改密码</a><hr></hr></th>
			</tr>
			<tr>
				<th><a href="my.action?opttype=queryMycourse">我的课程</a><hr></hr></th>
			</tr>
			<tr>
				<th><a href="my.action?opttype=queryMyblog">我的博客</a><hr></hr></th>
			</tr>
			<tr>
				<th><a href="my.action?opttype=updownload">我的作业</a><hr></hr></th>
			</tr>
		</table>
	</div>
	<div id="main">
		<div class="page">
			<c:forEach var="c" items="${hlist}">
				<form action="UploadServlet?hid=${c.hid }" enctype="multipart/form-data" method="post">
				    <table name="upanddown" border="1">
						<tr>
					    	<td>${c.hname }</td>
					    	<td>下载任务书：<a href="DownLoadServlet?hid=${c.hid }">下载</a></td>
					    	<td>上传文件：<input type="file" name="file"></td>
					    	<td><button type="submit" value='提交'>提交</button></td>
				    	</tr>
					</table>
				</form>
			</c:forEach>
		</div>
	</div>
</div>
</body>
</html>-->