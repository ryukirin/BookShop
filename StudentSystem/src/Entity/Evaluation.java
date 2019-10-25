package Entity;

public class Evaluation {
	private String eid;
	private String stars;
	private String uid;
	private String bid;
	public Evaluation(String eid, String stars, String uid, String bid) {
		super();
		this.eid = eid;
		this.stars = stars;
		this.uid = uid;
		this.bid = bid;
	}
	public Evaluation() {
		super();
	}
	public String getEid() {
		return eid;
	}
	public void setEid(String eid) {
		this.eid = eid;
	}
	public String getStars() {
		return stars;
	}
	public void setStars(String stars) {
		this.stars = stars;
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
