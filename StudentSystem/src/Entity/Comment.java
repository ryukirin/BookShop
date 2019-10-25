package Entity;

public class Comment {
	private String cid;
	private String cont;
	private String uid;
	private String bid;
	public Comment() {
		super();
	}
	public Comment(String cid, String cont, String uid, String bid) {
		super();
		this.cid = cid;
		this.cont = cont;
		this.uid = uid;
		this.bid = bid;
	}
	public String getCid() {
		return cid;
	}
	public void setCid(String cid) {
		this.cid = cid;
	}
	public String getCont() {
		return cont;
	}
	public void setCont(String cont) {
		this.cont = cont;
	}
	public String getUid() {
		return uid;
	}
	public void setUid(String uid) {
		this.uid = uid;
	}
	public String getBid() {
		return bid;
	}
	public void setBid(String bid) {
		this.bid = bid;
	}
}
