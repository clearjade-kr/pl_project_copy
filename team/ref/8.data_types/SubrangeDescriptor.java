// Type analysis

public class SubrangeDescriptor extends TypeDescriptor{

   public int lowerBound, upperBound;
   public TypeDescriptor superType;

   public SubrangeDescriptor(){
      super(SUBRANGE);
      lowerBound = upperBound = 0;
      superType = null;
   }

   public void setSuperType(TypeDescriptor t){
      superType = t;
   }

   public void setLowerAndUpper(int l, int u){
      lowerBound = l;
      upperBound = u;
   }

}