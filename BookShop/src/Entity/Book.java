package Entity;

public class Book {
	public Book(String bid, String bname, String publishers, String cont, String stock, String price, String tname,
			String url, String salenum) {
		super();
		this.bid = bid;
		this.bname = bname;
		this.publishers = publishers;
		this.cont = cont;
		this.stock = stock;
		this.price = price;
		this.tname = tname;
		this.url = url;
		this.salenum = salenum;
	}
	public Book() {
		super();
	}
	private String bid;
	private String bname;
	private String publishers;
	private String cont;
	private String stock;
	private String price;
	private String tname;
	private String url;
	private String salenum;
	public Book(String bname, String publishers, String cont, String stock, String price, String tname, String url) {
		super();
		this.bname = bname;
		this.publishers = publishers;
		this.cont = cont;
		this.stock = stock;
		this.price = price;
		this.tname = tname;
		this.url = url;
	}
	public Book(String bid, String bname, String publishers, String cont, String stock, String price, String tname, String url) {
		super();
		this.bid = bid;
		this.bname = bname;
		this.publishers = publishers;
		this.cont = cont;
		this.stock = stock;
		this.price = price;
		this.tname = tname;
		this.url = url;
	}
	public Book(String bid, String bname, String publishers, String stock, String price, String tname) {
		super();
		this.bid = bid;
		this.bname = bname;
		this.publishers = publishers;
		this.stock = stock;
		this.price = price;
		this.tname = tname;
	}
	public String getBid() {
		return bid;
	}
	public void setBid(String bid) {
		this.bid = bid;
	}
	public String getBname() {
		return bname;
	}
	public void setBname(String bname) {
		this.bname = bname;
	}
	public String getPublishers() {
		return publishers;
	}
	public void setPublishers(String publishers) {
		this.publishers = publishers;
	}
	public String getStock() {
		return stock;
	}
	public void setStock(String stock) {
		this.stock = stock;
	}
	public String getPrice() {
		return price;
	}
	public void setPrice(String price) {
		this.price = price;
	}
	public String getTname() {
		return tname;
	}
	public void setTname(String tname) {
		this.tname = tname;
	}
	public String getUrl() {
		return url;
	}
	public void setUrl(String url) {
		this.url = url;
	}
	public String getCont() {
		return cont;
	}
	public void setCont(String cont) {
		this.cont = cont;
	}
	public String getSalenum() {
		return salenum;
	}
	public void setSalenum(String salenum) {
		this.salenum = salenum;
	}
}
