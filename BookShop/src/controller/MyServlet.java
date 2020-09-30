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
		String uid,oldpwd,newpwd,anewpwd;
		uid = (String)request.getSession().getAttribute("uid");
		System.out.println(uid);
		switch(opttype){
		case "initMypage":
			request.getSession().setAttribute("uname", mdao.findUsername(uid));
			request.getSession().setAttribute("role", mdao.findUserrole(uid));
	    	response.sendRedirect("my.jsp");
		    break;
		case "queryMyorder":
			System.out.println(uid);
			request.getSession().setAttribute("molist", mdao.queryAllmyorder(uid));
			response.sendRedirect("myorder.jsp");
		    break;
		case "updatePwd":
			oldpwd = request.getParameter("oldpwd");
			newpwd = request.getParameter("newpwd");
			anewpwd = request.getParameter("anewpwd");
			request.setCharacterEncoding("gbk");
			PrintWriter out = response.getWriter();
			if(newpwd.equals(anewpwd) && dao.checkPwd(uid).equals(oldpwd)) {
				mdao.updatePwd(newpwd, uid);
				out.print("<script>alert('success!'); window.location='changepwd.jsp' </script>");
			}
			else if(!dao.checkPwd(uid).equals(oldpwd))
				out.print("<script>alert('password error!'); window.location='changepwd.jsp' </script>");
			else if(!newpwd.equals(anewpwd))
				out.print("<script>alert('check new password!'); window.location='changepwd.jsp' </script>");
			out.flush();
			out.close();
		    break;
		}
	}

	
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
			doGet(request, response);
	}
}