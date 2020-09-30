package Service;

import java.util.ArrayList;
import java.util.List;

import Entity.*;
import dbutil.SQLHelper;
import Service.AdminDao;

public class MyDao {
	/**
	 * query user name
	 * @param uid
	 * @return uname
	 */
	public String findUsername(String uid){
		String uname = null;
		String sql = "select uname from user where uid='"+uid+"'";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		if(!dblist.isEmpty()) {
			for(Object[] arr:dblist)
				uname = arr[0].toString();
		}
		return uname;
	}
	/**
	 * query user role
	 * @param uid
	 * @return uname
	 */
	public String findUserrole(String uid){
		String role = null;
		String sql = "select role from user where uid='"+uid+"'";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		if(!dblist.isEmpty()) {
			for(Object[] arr:dblist) {
				if(arr[0].toString().equals("1")) {
					role = "会员";
				}
				else if(arr[0].toString().equals("2")) {
					role = "管理员";
				}
			}
		}
		return role;
	}
	/**
	 * query all my order
	 * @param cid
	 * @return List<Order>
	 */
	public List<Order> queryAllmyorder(String uid){
		List<Order> olist = new ArrayList<Order>();
		String sql = "select bname,uname,price\r\n" + 
				"from book.orders,book.book,book.user\r\n" + 
				"where orders.uid = '"+uid+"' and orders.uid = user.uid and\r\n" + 
				"book.bid = orders.bid;";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Order order = new Order();
			order.setBname(arr[0].toString());
			order.setCname(arr[1].toString());
			order.setPrice(arr[2].toString());
			olist.add(order);
		}
		return olist;
	}
	/**
	 * update my password
	 * @param uid
	 * @return int column counts
	 */
	public int updatePwd(String pwd, String uid){
		String sql = "UPDATE user SET upwd='"+pwd+"' where uid='"+uid+"'";
		return SQLHelper.executeUpdate(sql);
	}
	/**
	 * buy book
	 * @param uid,bid
	 * @return int column counts
	 */
	public int buyBook(String bid, String uid){
		AdminDao dao = new AdminDao();
		int stock = Integer.parseInt(dao.queryaBookByid(bid).getStock())-1;
		String sql = "update book set stock='"+stock+"' where bid='"+bid+"';";
		SQLHelper.executeUpdate(sql);
		String sql1 = "INSERT INTO `book`.`orders` (`bid`, `uid`) VALUES ('"+bid+"', '"+uid+"');";
		return SQLHelper.executeUpdate(sql1);
	}
}
