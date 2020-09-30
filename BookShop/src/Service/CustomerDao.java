package Service;

import java.util.*;
import Entity.*;
import dbutil.SQLHelper;

public class CustomerDao {
	/**
	 * query all tag
	 * @param 
	 * @return List<Tag>
	 */
	public List<Tag> queryAlltag(){
		List<Tag> tlist = new ArrayList<Tag>();
		String sql = "select tname from tag";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Tag tag = new Tag();
			tag.setTname(arr[0].toString());
			tlist.add(tag);
		}
		return tlist;
	}
	/**
	 * query all book
	 * @param 
	 * @return List<Book>
	 */
	public List<Book> queryAllbook(){
		List<Book> blist = new ArrayList<Book>();
		String sql = "select bname, url, cont, price, IFNULL(count(orders.bid),0) as num,book.bid\r\n" + 
				"from book.tag, book.orders right outer join book.book\r\n" + 
				"on orders.bid = book.bid\r\n" + 
				"where book.tid = tag.tid\r\n" + 
				"group by bname, tname\r\n" + 
				"order by num DESC;";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Book book = new Book();
			book.setBname(arr[0].toString());
			book.setUrl(arr[1].toString());
			book.setCont(arr[2].toString());
			book.setPrice(arr[3].toString());
			book.setSalenum(arr[4].toString());
			book.setBid(arr[5].toString());
			blist.add(book);
		}
		return blist;
	}
	/**
	 * show book details
	 * @param 
	 * @return List<Book>
	 */
	public List<Book> showBook(String bid){
		List<Book> sblist = new ArrayList<Book>();
		String sql = "select bname, tname, publishers, cont, stock, price, url, IFNULL(count(orders.bid),0) as num, book.bid\r\n" + 
				"from book.tag, book.orders right outer join book.book\r\n" + 
				"on orders.bid = book.bid\r\n" + 
				"where book.tid = tag.tid and book.bid = '"+bid+"'\r\n" + 
				"group by bname, tname;";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Book book = new Book();
			book.setBname(arr[0].toString());
			book.setTname(arr[1].toString());
			book.setPublishers(arr[2].toString());
			book.setCont(arr[3].toString());
			book.setStock(arr[4].toString());
			book.setPrice(arr[5].toString());
			book.setUrl(arr[6].toString());
			book.setSalenum(arr[7].toString());
			book.setBid(arr[8].toString());
			sblist.add(book);
		}
		return sblist;
	}
	/**
	 * query book by name
	 * @param 
	 * @return List<Book>
	 */
	public List<Book> queryByName(String bname){
		List<Book> qbnlist = new ArrayList<Book>();
		String sql = "select bname, url, cont, price, IFNULL(count(orders.bid),0) as num,book.bid\r\n" + 
				"from book.tag, book.orders right outer join book.book\r\n" + 
				"on orders.bid = book.bid\r\n" + 
				"where book.tid = tag.tid and bname like '%"+bname+"%'\r\n" + 
				"group by bname, tname\r\n" + 
				"order by num DESC;";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Book book = new Book();
			book.setBname(arr[0].toString());
			book.setUrl(arr[1].toString());
			book.setCont(arr[2].toString());
			book.setPrice(arr[3].toString());
			book.setSalenum(arr[4].toString());
			book.setBid(arr[5].toString());
			qbnlist.add(book);
		}
		return qbnlist;
	}
	/**
	 * query book by tag
	 * @param 
	 * @return List<Book>
	 */
	public List<Book> queryByTag(String tname){
		List<Book> qbnlist = new ArrayList<Book>();
		String sql = "select bname, url, cont, price, IFNULL(count(orders.bid),0) as num, book.bid\r\n" + 
				"from book.tag, book.orders right outer join book.book\r\n" + 
				"on orders.bid = book.bid\r\n" + 
				"where book.tid = tag.tid and tname = '"+tname+"'\r\n" + 
				"group by bname, tname\r\n" + 
				"order by num DESC;";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Book book = new Book();
			book.setBname(arr[0].toString());
			book.setUrl(arr[1].toString());
			book.setCont(arr[2].toString());
			book.setPrice(arr[3].toString());
			book.setSalenum(arr[4].toString());
			book.setBid(arr[5].toString());
			qbnlist.add(book);
		}
		return qbnlist;
	}
}
