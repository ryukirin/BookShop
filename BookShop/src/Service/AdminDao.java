package Service;

import java.util.ArrayList;
import java.util.List;

import Entity.*;
import dbutil.SQLHelper;

public class AdminDao {
	/**
	 * query user by uid
	 * @param uid
	 * @return Users
	 */
	public Users queryUserById(String uid) {
		Users user = null;
		String sql = "select uid,uname,role from book.user where uid = '"+uid+"'";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		if(dblist.size()>0){
		    user = new Users();
		    Object[] arr=dblist.get(0);
			user.setUid(arr[0].toString());
			user.setName(arr[1].toString());
			user.setRole(arr[2].toString());
		}		
		return user;
	}
	/**
	 * query user by uname
	 * @param uname
	 * @return List<Users>
	 */
	public List<Users> queryUserByUname(String uname) {
		List<Users> ulist = new ArrayList<Users>();
		String sql = "select uid,uname,role \r\n" + 
				"from book.user\r\n" + 
				"where role = '1' and uname = '"+uname+"'";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Users user=new Users();
			user.setUid(arr[0].toString());
			user.setName(arr[1].toString());
			user.setRole(arr[2].toString());
			ulist.add(user);
		}
		return ulist;
	}
	/**
	 * query user by uname
	 * @param uname
	 * @return Users
	 */
	public Users queryUserByuname(String uname) {
		Users user=new Users();
		String sql = "select uid,uname,role \r\n" + 
				"from book.user\r\n" + 
				"where uname = '"+uname+"'";
		System.out.println(sql);
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			user.setUid(arr[0].toString());
			user.setName(arr[1].toString());
			user.setRole(arr[2].toString());
		}
		return user;
	}
	/**
	 * check user by uname,if have return false
	 * @param uname
	 * @return boolean
	 */
	public boolean checkUserByUname(String uname) {
		boolean flag = true;
		String sql = "select uid,uname,role from book.user where uname = '"+uname+"'";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		if(dblist.size()>0){
			flag = false;
		}		
		return flag;
	}
	/**
	 * query all customers
	 * @return
	 */
	public List<Users> queryCustomer() {
		List<Users> ulist = new ArrayList<Users>();
		String sql = "select uid,uname,role \r\n" + 
				"from book.user\r\n" + 
				"where role = '1'";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Users user=new Users();
			user.setUid(arr[0].toString());
			user.setName(arr[1].toString());
			user.setRole(arr[2].toString());
			ulist.add(user);
		}
		return ulist;
	}
	/**
	 * add customer
	 * @param User
	 * @return int column counts
	 */
	public int addCustomers(Users user) {
		String sql = "INSERT INTO book.user (uname,upwd,role) VALUES ('"+user.getName()+"','"+user.getPwd()+"','"+user.getRole()+"');";
		SQLHelper.executeUpdate(sql);
		String uid = queryUserByuname(user.getName()).getUid();
		String sql1 = "INSERT INTO book.customer (uid) VALUES ('"+uid+"');";
		return SQLHelper.executeUpdate(sql1);
	}
	/**
	 * delete customer by uid
	 * @param uid
	 * @return int column counts
	 */
	public int deleteCustomerById(String uid) {
		String sql = "delete from customer where uid=?;";
		SQLHelper.executeUpdateByParams(sql,uid);
		String sql1 = "delete from user where  uid=?;";
		return SQLHelper.executeUpdateByParams(sql1,uid);
	}
	/**
	 * query tag by tid
	 * @param 
	 * @return List<Tag>
	 */
	public String queryTagByTname(String tname){
		String tid = null;
		String sql = "select tid from tag where tname = '"+tname+"';";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			tid = arr[0].toString();
		}
		return tid;
	}
	/**
	 * add book
	 * @param Book
	 * @return int column counts
	 */
	public int addBook(Book book) {
		String sql = "INSERT INTO `book`.`book` (`bname`, `publishers`, `stock`, `price`, `tid`, `url`, `cont`) "
				+ "VALUES ('"+book.getBname()+"', '"+book.getPublishers()+"', '"+book.getStock()+"',"
				+ " '"+book.getPrice()+"', '"+queryTagByTname(book.getTname())+"', '"+book.getUrl()+"', '"+book.getCont()+"');";
		System.out.println(sql);
		return SQLHelper.executeUpdate(sql);
	}
	/**
	 * query all book
	 * @param 
	 * @return List<Book>
	 */
	public List<Book> queryAllbook(){
		List<Book> blist = new ArrayList<Book>();
		String sql = "select book.bid, bname, tname, publishers, cont, stock, price, IFNULL(count(orders.bid),0) as num\r\n" + 
				"from book.tag, book.orders right outer join book.book\r\n" + 
				"on orders.bid = book.bid\r\n" + 
				"where book.tid = tag.tid\r\n" + 
				"group by bname, tname\r\n" + 
				"order by book.bid ASC;";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Book book = new Book();
			book.setBid(arr[0].toString());
			book.setBname(arr[1].toString());
			book.setTname(arr[2].toString());
			book.setPublishers(arr[3].toString());
			book.setCont(arr[4].toString());
			book.setStock(arr[5].toString());
			book.setPrice(arr[6].toString());
			book.setSalenum(arr[7].toString());
			blist.add(book);
		}
		return blist;
	}
	/**
	 * query book by bname
	 * @param bname
	 * @return List<Book>
	 */
	public List<Book> queryBookByname(String bname){
		List<Book> blist = new ArrayList<Book>();
		String sql = "select book.bid, bname, tname, publishers, cont, stock, price, IFNULL(count(orders.bid),0) as num\r\n" + 
				"from book.tag, book.orders right outer join book.book\r\n" + 
				"on orders.bid = book.bid\r\n" + 
				"where book.tid = tag.tid and bname like '%"+bname+"%'\r\n" + 
				"group by bname, tname\r\n" + 
				"order by book.bid ASC;";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Book book = new Book();
			book.setBid(arr[0].toString());
			book.setBname(arr[1].toString());
			book.setTname(arr[2].toString());
			book.setPublishers(arr[3].toString());
			book.setCont(arr[4].toString());
			book.setStock(arr[5].toString());
			book.setPrice(arr[6].toString());
			book.setSalenum(arr[7].toString());
			blist.add(book);
		}
		return blist;
	}
	/**
	 * query book by id
	 * @param bname
	 * @return List<Book>
	 */
	public Book queryaBookByid(String bid){
		Book book = new Book();
		String sql = "select bid, bname, tname, publishers, cont, stock, price\r\n" + 
				"from book.tag ,book.book\r\n" + 
				"where book.tid = tag.tid and book.bid = '"+bid+"'";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			book.setBid(arr[0].toString());
			book.setBname(arr[1].toString());
			book.setTname(arr[2].toString());
			book.setPublishers(arr[3].toString());
			book.setCont(arr[4].toString());
			book.setStock(arr[5].toString());
			book.setPrice(arr[6].toString());
		}
		return book;
	}
	/**
	 * query book by id
	 * @param bname
	 * @return List<Book>
	 */
	public List<Book> queryBookByid(String bid){
		List<Book> blist = new ArrayList<Book>();
		String sql = "select bid, bname, tname, publishers, cont, stock, price\r\n" + 
				"from book.tag ,book.book\r\n" + 
				"where book.tid = tag.tid and book.bid = '"+bid+"'";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Book book = new Book();
			book.setBid(arr[0].toString());
			book.setBname(arr[1].toString());
			book.setTname(arr[2].toString());
			book.setPublishers(arr[3].toString());
			book.setCont(arr[4].toString());
			book.setStock(arr[5].toString());
			book.setPrice(arr[6].toString());
			blist.add(book);
		}
		return blist;
	}
	/**
	 * delete book by bid
	 * @param bid
	 * @return int column counts
	 */
	public int deleteBookById(String bid) {
		String sql = "delete from orders where bid=?;";
		SQLHelper.executeUpdateByParams(sql,bid);
		String sql1 = "delete from book where bid=?;";
		return SQLHelper.executeUpdateByParams(sql1,bid);
	}
	/**
	 * update book (only stock/publishers or price)
	 * @param bid,stock,publishers,price
	 * @return int column counts
	 */
	public int updateBook(String bid,String stock,String publishers,String price) {
		String sql1 = "update book set stock='"+stock+"' where bid='"+bid+"';";
		SQLHelper.executeUpdate(sql1);
		String sql2 = "update book set publishers='"+publishers+"' where bid='"+bid+"';";
		SQLHelper.executeUpdate(sql2);
		String sql3 = "update book set price='"+price+"' where bid='"+bid+"';";
		return SQLHelper.executeUpdate(sql3);
	}
	/**
	 * query all order
	 * @param 
	 * @return List<Order>
	 */
	public List<Order> queryAllorder(){
		List<Order> olist = new ArrayList<Order>();
		String sql = "select oid,bname,uname,price\r\n" + 
				"from book.orders,book.book,book.user \r\n" + 
				"where orders.uid = user.uid and book.bid = orders.bid;";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Order order = new Order();
			order.setOid(arr[0].toString());
			order.setBname(arr[1].toString());
			order.setCname(arr[2].toString());
			order.setPrice(arr[3].toString());
			olist.add(order);
		}
		return olist;
	}
	/**
	 * sum all order's price
	 * @param 
	 * @return sum price
	 */
	public float sumPrice() {
		float sum = 0;
		List<Order> olist = queryAllorder();
		for(int i=0;i<olist.size();i++) {
			float price = Float.parseFloat(olist.get(i).getPrice());
			sum = sum + price;
		}
		return sum;
	}
}
