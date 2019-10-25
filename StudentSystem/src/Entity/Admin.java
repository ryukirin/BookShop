package Entity;

public class Admin extends Users {
	private String id;
	private String ano;
	private String aname;
	public Admin(String id, String ano, String aname) {
		super();
		this.id = id;
		this.ano = ano;
		this.aname = aname;
	}
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	public String getAno() {
		return ano;
	}
	public void setAno(String ano) {
		this.ano = ano;
	}
	public String getAname() {
		return aname;
	}
	public void setAname(String aname) {
		this.aname = aname;
	}
}
