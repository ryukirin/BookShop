package Service;

import java.util.ArrayList;
import java.util.List;

import Entity.*;
import dbutil.SQLHelper;

public class MyDao {
	public List<Course> queryAllmycourse(String sno){
		List<Course> clist = new ArrayList<Course>();
		String sql = "select course.cno, cname, cla, cont,tname, count(sc.cno) as num\r\n" + 
				"	from course, teacher, sc\r\n" + 
				"	where course.tno = teacher.tno and sc.cno = course.cno and sno = '"+sno+"'\r\n" + 
				"	group by course.cno, cname, cla, tname";
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
	public List<Course> queryAllteacourse(String tno){
		List<Course> clist = new ArrayList<Course>();
		String sql = "select course.cno, cname, cla, cont,tname, count(sc.cno) as num\r\n" + 
				"	from course, teacher, sc\r\n" + 
				"	where course.tno = teacher.tno and sc.cno = course.cno course.tno = '"+tno+"'\r\n" + 
				"	group by course.cno, cname, cla, tname";
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
	public List<Course> queryMycourse(String sno){
		List<Course> mlist = new ArrayList<Course>();
		String sql = "select course.cno, cname, cla, cont,tname, count(sc.cno) as num\r\n" + 
				"from course, teacher, sc\r\n" + 
				"where course.tno = teacher.tno and sc.cno = course.cno and sno = '"+sno+"'\r\n" + 
				"group by course.cno, cname, cla, tname\r\n" + 
				"limit 2";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Course cou = new Course();
			cou.setCno(arr[0].toString());
			cou.setCname(arr[1].toString());
			cou.setCla(arr[2].toString());
			cou.setCont(arr[3].toString());
			cou.setTname(arr[4].toString());
			cou.setNum(arr[5].toString());
			mlist.add(cou);
		}
		return mlist;
	}
	public List<Course> queryTeacourse(String tno){
		List<Course> mlist = new ArrayList<Course>();
		String sql = "select course.cno, cname, cla, cont,tname, count(sc.cno) as num\r\n" + 
				"from course, teacher, sc\r\n" + 
				"where course.tno = teacher.tno and sc.cno = course.cno and course.tno = '"+tno+"'\r\n" + 
				"group by course.cno, cname, cla, tname\r\n" + 
				"limit 2";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Course cou = new Course();
			cou.setCno(arr[0].toString());
			cou.setCname(arr[1].toString());
			cou.setCla(arr[2].toString());
			cou.setCont(arr[3].toString());
			cou.setTname(arr[4].toString());
			cou.setNum(arr[5].toString());
			mlist.add(cou);
		}
		return mlist;
	}
	public List<Blog> queryMyblog(String sno){
		List<Blog> blist = new ArrayList<Blog>();
		String sql = "select blog.bid, bname, url, uname, count(distinct coid) as cnum, avg(stars) as eva, \r\n" + 
				"		tname,img\r\n" + 
				"from blog, comment, evaluation, tag, tbrelation, user\r\n" + 
				"where blog.bid = comment.bid and blog.bid = evaluation.bid and tbrelation.bid = blog.bid\r\n" + 
				"	and user.uid = blog.uid and tag.tid = tbrelation.tid and user.uid = '"+sno+"'\r\n" + 
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
			blist.add(blo);
		}
		return blist;
	}
	public List<Homework> queryMyhomework(String sno){
		List<Homework> hlist = new ArrayList<Homework>();
		String sql = "select hid, hname, gbook, cname\r\n" + 
				"from homework, sc, course\r\n" + 
				"where sc.cno = homework.cid and sc.sno = '"+sno+"' and course.cno = sc.cno";
		System.out.println(sql);
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Homework home = new Homework();
			home.setHid(arr[0].toString());
			home.setHname(arr[1].toString());
			home.setGbook(arr[2].toString());
			home.setCname(arr[3].toString());
			hlist.add(home);
		}
		return hlist;
	}
	public int addMyhomework(String sno,String hid, String filename){
		String sql = "INSERT INTO stuhomework (`book`, `sno`, `hid`) VALUES (?, ?, ?);";
		return SQLHelper.executeUpdateByParams(sql,filename,sno,hid);
	}
	public String queryMygbook(String hid){
		String filename = null;
		String sql = "select distinct hid, hname, gbook, cname\r\n" + 
				"from homework, sc, course\r\n" + 
				"where sc.cno = homework.cid and hid = '"+hid+"' and course.cno = sc.cno";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Homework home = new Homework();
			home.setHid(arr[0].toString());
			home.setHname(arr[1].toString());
			home.setGbook(arr[2].toString());
			home.setCname(arr[3].toString());
			filename = home.getGbook();
		}
		return filename;
	}
	public List<Stuhomework> queryBook(){
		List<Stuhomework> shlist = new ArrayList<Stuhomework>();
		String sql = "SELECT name, book, img, cname \r\n" + 
				"FROM stuhomework, students, homework, course\r\n" + 
				"where stuhomework.sno = students.sno and homework.cid = course.cno and stuhomework.hid = homework.hid;";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Stuhomework home = new Stuhomework();
			home.setSname(arr[0].toString());
			home.setHname(arr[1].toString());
			home.setImg(arr[2].toString());
			home.setCname(arr[3].toString());
			shlist.add(home);
		}
		return shlist;
	}
}
