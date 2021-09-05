// Type analysis

import java.util.*;

public class ArrayDescriptor extends TypeDescriptor{

   public TypeDescriptor baseType;
   private List<TypeDescriptor> indexTypes;

   public ArrayDescriptor(){
      super(ARRAY);
      baseType = new TypeDescriptor();
      indexTypes = new ArrayList<TypeDescriptor>();
   }

   public void setIndexType(TypeDescriptor t){
      indexTypes.add(t);
   }

   public void setBaseType(TypeDescriptor t){
      baseType = t;
   }

   public Iterator<TypeDescriptor> getIndexTypes(){
      return indexTypes.iterator();
   }

}