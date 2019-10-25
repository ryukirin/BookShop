package controller;

import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import Entity.*;
import Service.AdminDao;

@SuppressWarnings("serial")
@WebServlet("/jsp/admin.action")
public class AdminServlet extends HttpServlet {
	private AdminDao dao=new AdminDao();
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		String opttype=request.getParameter("opttype");
		String uid="",name,role;
		switch(opttype){
		case "queryAll":
			 request.getSession().setAttribute("clist", dao.queryUsers());
			 response.sendRedirect("admin.jsp");
		    break;
		case "add":
			uid=request.getParameter("uid");
			 name=request.getParameter("uname");
			 role=request.getParameter("role");
			if(dao.addUsers(new Users(uid,name,role))>0)
				response.sendRedirect("admin.action?opttype=queryAll");
			break;
		case "delete":
		    uid=request.getParameter("uid");
		    if(dao.deleteUsersById(uid)>0)
				response.sendRedirect("admin.action?opttype=queryAll");
		    break;
		case "edit":
		    uid=request.getParameter("id");
		    Users user=dao.queryUserById(uid);
		    request.getSession().setAttribute("c", user);
		    response.sendRedirect("useredit.jsp");
		    break;
		case "update":
		     uid=request.getParameter("uid");
		     name=request.getParameter("name");
			 role=request.getParameter("role");
		     if(dao.updateUsers(uid, name, role)>0){
		    	 response.sendRedirect("admin.action?opttype=queryAll");
		     }
		    break;
		}
	}

	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request, response);
	}

}
