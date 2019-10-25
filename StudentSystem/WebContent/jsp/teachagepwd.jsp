<%@ page language="java" pageEncoding="utf-8"%> 
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>更改密码</title>
<link rel="stylesheet" type="text/css" href="../css/changepwd.css"></link>

</head>
 
<body>
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
				<th><a href="teachagepwd.jsp">修改密码</a><hr></hr></th>
			</tr>
			<tr>
				<th><a href="my.action?opttype=queryMycourse">我的课程</a><hr></hr></th>
			</tr>
			<tr>
				<th><a href="my.action?opttype=queryMyblog">我的博客</a><hr></hr></th>
			</tr>
			<tr>
				<th><a href="#">申请开班</a><hr></hr></th>
			</tr>
		</table>
	</div>
	<div id="main">
		<div class="page">
			<form action="my.action?opttype=updatePwd" name="pwdform" method="post">
				<table align="center" class="pwdtable">
					<tr>
						<td>原密码：</td>
						<td align="left" >
							<input type="password" name="oldpwd" id="name" required="required">
						</td>
					</tr>
					<tr>
						<td>新密码:</td>
						<td align="left">
							<input type="password" name="newpwd" id="passwd" required="required">
						</td>
					</tr>
					<tr>
						<td>确认新密码:</td>
						<td align="left">
							<input type="password" name="anewpwd" id="passwd" required="required">
						</td>
					</tr>
					<tr>
						<td align="center" colspan="2">
							<button type="submit" value="login">确认</button>
						</td>
					</tr>
				</table>
			</form>
		</div>
	</div>
</div>
	
</body>
</html>