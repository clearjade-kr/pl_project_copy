// Type analysis

public class TypeDescriptor extends Object{

   public static final int NONE = 0;
   public static final int ARRAY = 1;
   public static final int ENUM = 2;
   public static final int SUBRANGE = 3;

   public int form;

   public TypeDescriptor(int newForm){
      form = newForm;
   }
    
   public TypeDescriptor(){
      this(NONE);
   }

   public String toString(){
      return formToString();
   }

   private String formToString(){
      if (form == NONE)
         return "NONE";
      else if (form == ARRAY)
         return "ARRAY";
      else if (form == ENUM)
         return "ENUM";
      else if (form == SUBRANGE)
         return "SUBRANGE";
      else
         return "RECORD";
   }

}