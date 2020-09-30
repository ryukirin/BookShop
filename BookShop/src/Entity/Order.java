package Entity;

public class Order {
	public Order() {
		super();
	}
	private String oid;
	private String bname;
	private String cname;
	private String price;
	public Order(String oid, String bname, String cname, String price) {
		super();
		this.oid = oid;
		this.bname = bname;
		this.cname = cname;
		this.price = price;
	}
	public String getOid() {
		return oid;
	}
	public void setOid(String oid) {
		this.oid = oid;
	}
	public String getBname() {
		return bname;
	}
	public void setBname(String bname) {
		this.bname = bname;
	}
	public String getCname() {
		return cname;
	}
	public void setCname(String cname) {
		this.cname = cname;
	}
	public String getPrice() {
		return price;
	}
	public void setPrice(String price) {
		this.price = price;
	}
}
