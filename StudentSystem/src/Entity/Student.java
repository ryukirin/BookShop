package Entity;

public class Student extends Users {
	private String id;
	private String sno;
	private String sname;
	public Student(String id, String sno, String sname) {
		super();
		this.id = id;
		this.sno = sno;
		this.sname = sname;
	}
	public Student() {
		super();
	}
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	public String getSno() {
		return sno;
	}
	public void setSno(String sno) {
		this.sno = sno;
	}
	public String getSname() {
		return sname;
	}
	public void setSname(String sname) {
		this.sname = sname;
	}
}
