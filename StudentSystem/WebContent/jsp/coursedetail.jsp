<%@ page language="java" pageEncoding="utf-8"%> 
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<c:forEach var="c" items="${cdlist}">
			<title>${c.cname }</title>
		</c:forEach>
	</head>
	<body>
		<div>
			<c:forEach var="c" items="${cdlist}">
				<h1 align="center">${c.cname }</h1>
				<h3 align="center">教师：${c.tname }&nbsp&nbsp&nbsp&nbsp分类 ：${c.cla }</h3><hr></hr>
				<p align="center">${c.cont }</p>
			</c:forEach>
		</div>
		<div>
			<table border="1" bordercolor="lightgray" width="100%" align="center">
				<tr>
					<td align="center">课程大纲</td>
				</tr>
				<tr>
					<td>第一章</td>
				</tr>
				<tr>
					<td>第二章</td>
				</tr>
			</table>
		</div></br>
		<div>
			<table border="1" bordercolor="lightgray" width="100%" align="center">
				<tr>
					<td align="center">进度表</td>
				</tr>
				<tr>
					<td>第一周</td>
				</tr>
				<tr>
					<td>第二周</td>
				</tr>
			</table>
		</div>
	</body>
</html>
