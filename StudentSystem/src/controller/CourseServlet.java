package controller;

import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import Service.StudentDao;

@SuppressWarnings("serial")
@WebServlet("/jsp/course.action")

public class CourseServlet extends HttpServlet {
	private StudentDao dao = new StudentDao();
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		String opttype=request.getParameter("opttype");
		String cla,cname,tname,cno;
		switch(opttype){
		case "queryAllcourse":
		    request.getSession().setAttribute("tlist", dao.queryAllcla());
		    request.getSession().setAttribute("clist", dao.queryAllcourse());
			response.sendRedirect("course.jsp");
		    break;
		case "queryByname":
			cname = request.getParameter("cname");
		    request.getSession().setAttribute("tlist", dao.queryAllcla());
			request.getSession().setAttribute("clist", dao.queryByName(cname));
			response.sendRedirect("course.jsp");
		    break;
		case "queryBycla":
			cla=request.getParameter("cla");
		    request.getSession().setAttribute("tlist", dao.queryAllcla());
			request.getSession().setAttribute("clist", dao.queryByClass(cla));
			response.sendRedirect("course.jsp");
		    break;
		case "queryBytea":
		    tname=request.getParameter("tname");
		    request.getSession().setAttribute("tlist", dao.queryAllcla());
		    request.getSession().setAttribute("clist", dao.queryByTeacher(tname));
			response.sendRedirect("course.jsp");
		    break;
		case "courseDetail":
		    cno=request.getParameter("cno");
		    request.getSession().setAttribute("cdlist", dao.showCourse(cno));
			response.sendRedirect("coursedetail.jsp");
		    break;
		}
	}

	
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
			doGet(request, response);
	}
}