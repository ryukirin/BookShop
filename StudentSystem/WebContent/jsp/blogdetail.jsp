<%@ page language="java" pageEncoding="utf-8"%> 
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<c:forEach var="c" items="${bdlist}">
			<title>${c.bname }</title>
		</c:forEach>
	</head>
	<body>
		<div>
			<c:forEach var="c" items="${bdlist}">
				<h1 align="center">${c.bname }</h1>
				<h3 align="center">发布者：${c.uname }&nbsp&nbsp&nbsp&nbsp标签 ：${c.tname }</h3><hr></hr>
				<p>${c.url }</p>
			</c:forEach>
		</div>
	</body>
</html>
