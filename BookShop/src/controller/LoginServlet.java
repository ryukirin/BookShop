package controller;

import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import Entity.Users;
import Service.SystemDao;
import Service.AdminDao;;

@SuppressWarnings("serial")
@WebServlet("/login.action")

public class LoginServlet extends HttpServlet {
	private SystemDao dao = new SystemDao();
	private AdminDao adao = new AdminDao();
	HttpSession session = null;
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		String opttype=request.getParameter("opttype");
		String uid=null,upwd,uname,checkpwd;
		switch(opttype){
		case "addusers":
			request.setCharacterEncoding("utf-8");
			uname = request.getParameter("inputUname");
			request.setCharacterEncoding("utf-8");
			upwd = request.getParameter("inputPassword");
			request.setCharacterEncoding("utf-8");
			checkpwd = request.getParameter("checkPassword");
			PrintWriter out = response.getWriter();
			if(!adao.checkUserByUname(uname))
				out.print("<script>alert('please change uer name!'); window.location='register.jsp' </script>");
			else if(!upwd.equals(checkpwd))
				out.print("<script>alert('please check password!'); window.location='register.jsp' </script>");
			else{
				Users user = new Users(uname,upwd,"1");
			    if(adao.addCustomers(user)>0)
					response.sendRedirect("login.jsp");
			    else
			    	out.print("<script>alert('fail,try again!'); window.location='register.jsp' </script>");
			}
		    break;
		case "checkUsers":
			uid=adao.queryUserByuname(request.getParameter("inputName")).getUid();
			upwd=request.getParameter("inputPassword");
			PrintWriter out1 = response.getWriter();
			if(dao.checkUsers(uid, upwd) != null) {
				System.out.println(dao.checkRoles(uid)); 
				if(dao.checkRoles(uid).equals("1")) {
					response.sendRedirect("index.jsp");
				}
				else if (dao.checkRoles(uid).equals("2")) {
					response.sendRedirect("jsp/admin.action?opttype=queryAllcustomers");
				}
				request.getSession().setAttribute("uid", dao.checkUsers(uid,upwd));
				request.getSession().setAttribute("role", dao.checkRoles(uid));//1:会员，2:管理员
			}
			else
				out1.print("<script>alert('username or password error!'); window.location='login.jsp' </script>");
		    break;
		}
	}

	
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
			doGet(request, response);
	}
}