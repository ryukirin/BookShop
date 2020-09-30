package filter;

import java.io.IOException;
import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class MyFilter implements Filter {

	public void destroy() {
		System.out.println("destroy()");
	}

	public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) 
			throws IOException, ServletException {
		System.out.println("doFilter()");
		HttpServletRequest req1 = (HttpServletRequest)req;
		if(req1.getSession().getAttribute("uid")==null) {
			HttpServletResponse res1 = (HttpServletResponse)res;
			res1.sendRedirect("../login.jsp");
		}
		else
			chain.doFilter(req, res);
	}

	public void init(FilterConfig fConfig) throws ServletException {
		System.out.println("init()");
	}

}
