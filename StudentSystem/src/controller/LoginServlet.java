package controller;

import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import Service.SystemDao;

@SuppressWarnings("serial")
@WebServlet("/login.action")

public class LoginServlet extends HttpServlet {
	private SystemDao dao = new SystemDao();
	HttpSession session = null;
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		String opttype=request.getParameter("opttype");
		String uid=null,upwd;
		switch(opttype){
		case "checkUsers":
			uid = "1";
			upwd = "1";
			request.getSession().setAttribute("uid", "1");
			/*暂时版本，后期补全
			uid=request.getParameter("inputName");
			upwd=request.getParameter("inputPassword");
			
			 * if(dao.checkUsers(uid, upwd) != null) {
				request.getSession().setAttribute("uid", dao.checkUsers(uid,upwd));
				request.getSession().setAttribute("role", dao.checkRoles(uid));//1:学生，2:老师，3:管理员
				if(dao.checkRoles(uid).equals("1") || dao.checkRoles(uid).equals("2"))
					response.sendRedirect("jsp/course.action?opttype=queryAllcourse");
				else if (dao.checkRoles(uid).equals("3"))
					response.sendRedirect("jsp/admin.action?opttype=queryAll");
			}*/
			response.sendRedirect("jsp/admin.jsp");
		    break;
		}
	}

	
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
			doGet(request, response);
	}
}