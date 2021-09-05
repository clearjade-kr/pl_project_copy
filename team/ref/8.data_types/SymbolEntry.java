import java.util.*;

public class SymbolEntry extends Object{

   // Identifier roles
   public static final int NONE = 0;
   public static final int CONST = 1;
   public static final int PARAM = 2;
   public static final int PROC = 3;
   public static final int TYPE = 4;
   public static final int VAR = 5;
   // Parameter modes
   public static final int IN = 6;
   public static final int OUT = 7;
   public static final int IN_OUT = 8;

   /*
   All identifiers have a name, role, and type.
   Procedures have a parameter list.
   Constants have a value.
   Parameters have a mode.
   Identifiers can be in a list (using next)
   */

   public String name;
   public int role, mode, value;
   public SymbolEntry next;
   public List<SymbolEntry> parameterList;
   public TypeDescriptor type;

   public SymbolEntry(String id){
      name = id;
      role = NONE;
      next = null;
      value = 0;
      mode = NONE;
      parameterList = new ArrayList<SymbolEntry>();
      type = new TypeDescriptor();
   }

   // Copy constructor
   public SymbolEntry(SymbolEntry se){
      name = se.name;
      role = se.role;
      next = se.next;
      value = se.value;
      mode = se.mode;
      parameterList = se.parameterList;
      type = se.type;
   }

   public String toString(){
      return "Name: " + name + "\n" + "Role: " + roleToString() + "\n" +
             "Type: " + type;
   }

   public void setRole(int r){
      role = r;
      if (next != null)
         next.setRole(r);
   }

   public void setType(TypeDescriptor t){
      type = t;
      if (next != null)
         next.setType(t);
   }

   public void setParameters(SymbolEntry list){
      while (list != null){
         parameterList.add(list);
         list = list.next;
      }
   }

   public void setValue(int v){
      value = v;
      if (next != null)
         next.setValue(v);
   }

   public void setMode(int m){
      mode = m;
      if (next != null)
         next.setMode(m);
   }

   public Iterator<SymbolEntry> getParameters(){
      return parameterList.iterator();
   }

   public void append(SymbolEntry entry){
      if (next == null)
         next = entry;
      else
         next.append(entry);
   }

   private String roleToString(){
      String s = "";
      switch (role){
         case NONE:  s = "None";      break;
         case CONST: s = "CONSTANT";  break;
         case PARAM: s = "PARAMETER"; break;
         case PROC:  s = "PROCEDURE"; break;
         case TYPE:  s = "TYPE";      break;
         case VAR:   s = "VARIABLE";  break;
         default:    s = "None";
      }
      return s;
   }

}