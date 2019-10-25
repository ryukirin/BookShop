package Service;

import java.util.*;
import Entity.*;
import dbutil.SQLHelper;

public class StudentDao {
	public List<Cla> queryAllcla(){
		List<Cla> tlist = new ArrayList<Cla>();
		String sql = "select cla from cla";//不一定对
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Cla cla = new Cla();
			cla.setCla(arr[0].toString());
			tlist.add(cla);
		}
		return tlist;
	}
	public List<Tag> queryAlltag(){
		List<Tag> tlist = new ArrayList<Tag>();
		String sql = "select tname from tag";//不一定对
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Tag tag = new Tag();
			tag.setTname(arr[0].toString());
			tlist.add(tag);
		}
		return tlist;
	}
	public List<Course> queryAllcourse(){
		List<Course> clist = new ArrayList<Course>();
		String sql = "select course.cno, cname, cla, cont, tname, count(sc.cno) as num\r\n" + 
				"from course, teacher, sc\r\n" + 
				"where course.tno = teacher.tno and sc.cno = course.cno\r\n" + 
				"group by course.cno, cname, cla, tname\r\n"
				+ "order by num DESC";//不一定对
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Course cou = new Course();
			cou.setCno(arr[0].toString());
			cou.setCname(arr[1].toString());
			cou.setCla(arr[2].toString());
			cou.setCont(arr[3].toString());
			cou.setTname(arr[4].toString());
			cou.setNum(arr[5].toString());
			clist.add(cou);
		}
		return clist;
	}
	public List<Course> showCourse(String cno){
		List<Course> cdlist = new ArrayList<Course>();
		String sql = "select course.cno, cname, cla, cont, tname, count(sc.cno) as num\r\n" + 
				"from course, teacher, sc\r\n" + 
				"where course.tno = teacher.tno and sc.cno = course.cno and course.cno = '"+cno+"'\r\n" + 
				"group by course.cno, cname, cla, tname;";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Course cou = new Course();
			cou.setCno(arr[0].toString());
			cou.setCname(arr[1].toString());
			cou.setCla(arr[2].toString());
			cou.setCont(arr[3].toString());
			cou.setTname(arr[4].toString());
			cou.setNum(arr[5].toString());
			cdlist.add(cou);
		}
		return cdlist;
	}
	public List<Blog> queryAllblog(){
		List<Blog> blist = new ArrayList<Blog>();
		String sql = "select blog.bid, bname, url, uname, count(distinct coid) as cnum, IFNULL(avg(stars),0) as eva, tname,img\r\n" + 
				"from tag, tbrelation, user, comment inner join evaluation right outer join blog\r\n" + 
				"on blog.bid = comment.bid and blog.bid = evaluation.bid\r\n" + 
				"where user.uid = blog.uid and tbrelation.bid = blog.bid\r\n" + 
				"and tag.tid = tbrelation.tid\r\n" + 
				"group by blog.bid\r\n" + 
				"order by eva DESC";//不一定对
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Blog blo = new Blog();
			blo.setBid(arr[0].toString());
			blo.setBname(arr[1].toString());
			blo.setUrl(arr[2].toString());
			blo.setUname(arr[3].toString());
			blo.setCnum(arr[4].toString());
			blo.setEva(arr[5].toString());
			blo.setTname(arr[6].toString());
			blo.setImg(arr[7].toString());
			blist.add(blo);
		}
		return blist;
	}//查找所有博客
	public List<Blog> showBlog(String bid){
		List<Blog> bdlist = new ArrayList<Blog>();
		String sql = "select blog.bid, bname, url, uname, count(distinct coid) as cnum, IFNULL(avg(stars),0) as eva, tname, img \r\n" + 
				"from tag, tbrelation, user, comment inner join evaluation right outer join blog\r\n" + 
				"on blog.bid = comment.bid and blog.bid = evaluation.bid\r\n" + 
				"where user.uid = blog.uid and tbrelation.bid = blog.bid\r\n" + 
				"and tag.tid = tbrelation.tid and blog.bid='"+bid+"'\r\n" + 
				"group by blog.bid\r\n" + 
				"order by eva DESC";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Blog blo = new Blog();
			blo.setBid(arr[0].toString());
			blo.setBname(arr[1].toString());
			blo.setUrl(arr[2].toString());
			blo.setUname(arr[3].toString());
			blo.setCnum(arr[4].toString());
			blo.setEva(arr[5].toString());
			blo.setTname(arr[6].toString());
			blo.setImg(arr[7].toString());
			bdlist.add(blo);
		}
		return bdlist;
	}
	public List<Course> queryByName(String cname){
		List<Course> clist = new ArrayList<Course>();
		String sql = "select course.cno, cname, cla, cont, tname, count(sc.cno) as num\r\n" + 
				"from course, teacher, sc\r\n" + 
				"where Cname = '"+cname+"' and course.tno = teacher.tno and sc.cno = course.cno\r\n" + 
				"group by course.cno, cname, cla, tname\r\n"
				+ "order by num DESC;";//不一定对
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Course cou = new Course();
			cou.setCno(arr[0].toString());
			cou.setCname(arr[1].toString());
			cou.setCla(arr[2].toString());
			cou.setCont(arr[3].toString());
			cou.setTname(arr[4].toString());
			cou.setNum(arr[5].toString());
			clist.add(cou);
		}
		return clist;
	}
	public List<Course> queryByClass(String cla){
		List<Course> clist = new ArrayList<Course>();
		String sql = "select course.cno, cname, cla, cont, tname, count(sc.cno) as num\r\n" + 
				"from course, teacher, sc\r\n" + 
				"where cla = '"+cla+"' and course.tno = teacher.tno and sc.cno = course.cno\r\n" + 
				"group by course.cno, cname, cla, tname\r\n"
				+ "order by num DESC;";//不一定对
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Course cou = new Course();
			cou.setCno(arr[0].toString());
			cou.setCname(arr[1].toString());
			cou.setCla(arr[2].toString());
			cou.setCont(arr[3].toString());
			cou.setTname(arr[4].toString());
			cou.setNum(arr[5].toString());
			clist.add(cou);
		}
		return clist;
	}
	//通过分类查课程
	public List<Course> queryByTeacher(String tname){
		List<Course> clist = new ArrayList<Course>();
		String sql = "select course.cno, cname, cla, cont, tname, count(sc.cno) as num\r\n" + 
				"from course, teacher, sc\r\n" + 
				"where tname = '"+tname+"' and course.tno = teacher.tno and sc.cno = course.cno\r\n" + 
				"group by course.cno, cname, cla, tname\r\n"
				+ "order by num DESC;";//不一定对
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Course cou = new Course();
			cou.setCno(arr[0].toString());
			cou.setCname(arr[1].toString());
			cou.setCla(arr[2].toString());
			cou.setCont(arr[3].toString());
			cou.setTname(arr[4].toString());
			cou.setNum(arr[5].toString());
			clist.add(cou);
		}
		return clist;
	}
	//通过老师查课程
	
	public List<Blog> queryByUser(String uname){
		List<Blog> blist = new ArrayList<Blog>();
		String sql = "select blog.bid, bname, url, uname, count(distinct coid) as cnum, IFNULL(avg(stars),0) as eva, tname,img \r\n" + 
				"from tag, tbrelation, user, comment inner join evaluation right outer join blog\r\n" + 
				"on blog.bid = comment.bid and blog.bid = evaluation.bid\r\n" + 
				"where user.uid = blog.uid and tbrelation.bid = blog.bid\r\n" + 
				"and tag.tid = tbrelation.tid and uname = '"+uname+"'\r\n" + 
				"group by blog.bid\r\n" + 
				"order by eva DESC";//不一定对
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Blog blo = new Blog();
			blo.setBid(arr[0].toString());
			blo.setBname(arr[1].toString());
			blo.setUrl(arr[2].toString());
			blo.setUname(arr[3].toString());
			blo.setCnum(arr[4].toString());
			blo.setEva(arr[5].toString());
			blo.setTname(arr[6].toString());
			blo.setImg(arr[7].toString());
			blist.add(blo);
		}
		return blist;
	}
	//通过发布者查博客
	public List<Blog> queryByBname(String bname){
		List<Blog> blist = new ArrayList<Blog>();
		String sql = "select blog.bid, bname, url, uname, count(distinct coid) as cnum, IFNULL(avg(stars),0) as eva, tname,img \r\n" + 
				"from tag, tbrelation, user, comment inner join evaluation right outer join blog\r\n" + 
				"on blog.bid = comment.bid and blog.bid = evaluation.bid\r\n" + 
				"where user.uid = blog.uid and tbrelation.bid = blog.bid\r\n" + 
				"and tag.tid = tbrelation.tid and bname like '%"+bname+"%'\r\n" + 
				"group by blog.bid\r\n" + 
				"order by eva DESC";//不一定对
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Blog blo = new Blog();
			blo.setBid(arr[0].toString());
			blo.setBname(arr[1].toString());
			blo.setUrl(arr[2].toString());
			blo.setUname(arr[3].toString());
			blo.setCnum(arr[4].toString());
			blo.setEva(arr[5].toString());
			blo.setTname(arr[6].toString());
			blo.setImg(arr[7].toString());
			blist.add(blo);
		}
		return blist;
	}
	//通过博客标题查博客
	public List<Blog> queryByTag(String tname){
		List<Blog> blist = new ArrayList<Blog>();
		String sql = "select blog.bid, bname, url, uname, count(distinct coid) as cnum, IFNULL(avg(stars),0) as eva, tname,img \r\n" + 
				"from tag, tbrelation, user, comment inner join evaluation right outer join blog\r\n" + 
				"on blog.bid = comment.bid and blog.bid = evaluation.bid\r\n" + 
				"where user.uid = blog.uid and tbrelation.bid = blog.bid\r\n" + 
				"and tag.tid = tbrelation.tid and tname = '"+tname+"'\r\n" + 
				"group by blog.bid\r\n" + 
				"order by eva DESC";//不一定对
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Blog blo = new Blog();
			blo.setBid(arr[0].toString());
			blo.setBname(arr[1].toString());
			blo.setUrl(arr[2].toString());
			blo.setUname(arr[3].toString());
			blo.setCnum(arr[4].toString());
			blo.setEva(arr[5].toString());
			blo.setTname(arr[6].toString());
			blo.setImg(arr[7].toString());
			blist.add(blo);
		}
		return blist;
	}
	//通过标签查博客
	public int updateStudentPwd(String pwd, String uid) {
		String sql = "update user set pwd=? where uid=?";	
		return SQLHelper.executeUpdateByParams(sql, pwd,uid);
	}
	//修改自己的密码，未修
	public int addComm(Comment comm) {
		String sql = "insert into comment values('" + comm.getCid() + "','" + comm.getCont() 
					+ "','" + comm.getUid() + "','" + comm.getBid() + "')";
		return SQLHelper.executeUpdate(sql);
	}
	//发表评论，未修
	public int addEva(Evaluation eva) {
		String sql = "insert into comment values('" + eva.getEid() + "','" + eva.getStars() 
					+ "','" + eva.getUid() + "','" + eva.getBid() + "')";
		return SQLHelper.executeUpdate(sql);
	}
}
