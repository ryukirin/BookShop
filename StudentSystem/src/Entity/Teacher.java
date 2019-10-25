package Entity;

public class Teacher extends Users {
	private String id;
	private String tno;
	private String tname;
	public Teacher(String id, String tno, String tname) {
		super();
		this.id = id;
		this.tno = tno;
		this.tname = tname;
	}
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	public String getTno() {
		return tno;
	}
	public void setTno(String tno) {
		this.tno = tno;
	}
	public String getTname() {
		return tname;
	}
	public void setTname(String tname) {
		this.tname = tname;
	}
}
