package controller;

import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import Service.SystemDao;
import Service.MyDao;

@SuppressWarnings("serial")
@WebServlet("/jsp/my.action")

public class MyServlet extends HttpServlet {
	private SystemDao dao = new SystemDao();
	private MyDao mdao = new MyDao();
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		String opttype=request.getParameter("opttype");
		String uid,oldpwd,newpwd,anewpwd,role,hid;
		uid = (String)request.getSession().getAttribute("uid");
		role = (String)request.getSession().getAttribute("role");//1:学生，2:老师，3:管理员
	   System.out.println(role);
		switch(opttype){
		case "initMypage":
			if(role.equals("1")) {
				request.getSession().setAttribute("clist", mdao.queryAllmycourse(uid));
		    	request.getSession().setAttribute("nlist", dao.queryAllnote());
		    	response.sendRedirect("my.jsp");
			}
		    else if(role.equals("2")) {
		    	request.getSession().setAttribute("clist", mdao.queryAllteacourse(uid));
		    	request.getSession().setAttribute("nlist", dao.queryAllnote());
		    	response.sendRedirect("teamy.jsp");
		    }
		    break;
		case "queryMycourse":  
			if(role.equals("1")) {
				request.getSession().setAttribute("mlist", mdao.queryMycourse(uid));
		    	response.sendRedirect("mycourse.jsp");}
		    else if(role.equals("2")) {
		    	request.getSession().setAttribute("mlist", mdao.queryTeacourse(uid));
		    	response.sendRedirect("teamycourse.jsp");
		    }
		    break;
		case "queryMyblog":
			if(role.equals("1")) {
				request.getSession().setAttribute("blist", mdao.queryMyblog(uid));
				response.sendRedirect("myblog.jsp");
			}
			else if(role.equals("2")) {
				request.getSession().setAttribute("blist", mdao.queryMyblog(uid));
				response.sendRedirect("teamyblog.jsp");
			}
		    break;
		case "updatePwd":
			oldpwd = request.getParameter("oldpwd");
			newpwd = request.getParameter("newpwd");
			anewpwd = request.getParameter("anewpwd");
			request.setCharacterEncoding("gbk");
			PrintWriter out = response.getWriter();
			if(newpwd.equals(anewpwd) && dao.checkPwd(uid).equals(oldpwd)) {
				dao.updatePwd(newpwd, uid);
				out.print("<script>alert('success!'); window.location='chagepwd.jsp' </script>");
			}
			else if(!dao.checkPwd(uid).equals(oldpwd))
				out.print("<script>alert('password error!'); window.location='chagepwd.jsp' </script>");
			else if(!newpwd.equals(anewpwd))
				out.print("<script>alert('check new password!'); window.location='chagepwd.jsp' </script>");
			out.flush();
			out.close();
		    break;
		case "updownload":
			request.getSession().setAttribute("hlist", mdao.queryMyhomework(uid));
	    	response.sendRedirect("upload.jsp");
		    break;
		case "findhomework":
			request.getSession().setAttribute("shlist", mdao.queryBook());
	    	response.sendRedirect("Sourse.jsp");
		    break;
		}
	}

	
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
			doGet(request, response);
	}
}