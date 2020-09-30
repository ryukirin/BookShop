package Entity;

public class Customer extends Users {
	private String cid;
	private String cname;
	public Customer(String cid, String cname) {
		super();
		this.cid = cid;
		this.cname = cname;
	}
	public Customer() {
		super();
	}
	public String getCid() {
		return cid;
	}
	public void setCid(String cid) {
		this.cid = cid;
	}
	public String getCname() {
		return cname;
	}
	public void setCname(String cname) {
		this.cname = cname;
	}
}
