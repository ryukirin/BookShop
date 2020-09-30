<%@ page language="java" import="java.io.*" pageEncoding="utf-8"%> 
<%
	String img=request.getParameter("img");
	String uploadPath = this.getServletContext().getRealPath("");
	System.out.println("当前服务器路径---->"+uploadPath);
	uploadPath = uploadPath+"img\\"+img;
	System.out.println("图片地址---->"+uploadPath);
	FileInputStream in = new FileInputStream(new File(uploadPath));
	OutputStream o = response.getOutputStream();
	int l = 0;
	byte[] buffer = new byte[4096];
	while((l = in.read(buffer)) != -1){
		o.write(buffer,0,l);
	}
	o.flush();
	in.close();
	o.close();
%>