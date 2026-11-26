# Style rules

- No fill on groups (`fillColor=none`). Exception: the EKS cluster box uses white fill so
  the dashed AZ lines behind it do not cross its text.
- Group colours: Region dashed #147EBA, VPC #248814, AZ dashed #545B64, public subnet
  #7AA116, private and database subnet #00A4A6, Auto Scaling group dashed #D86613.
- Subnets: remove `grStroke=0` from the official subnet style. Without a fill it hides
  the border.
- Arrows: orthogonal, `endArrow=open`, width 2.5 to 3. Public traffic orange #E8590C,
  private traffic green #2E7D32, neutral grey #545B64. Dashed means standby, replication,
  DNS or optional. Add a small legend.
- Labels: plain weight, very simple English, at most two short lines. Do not put
  `whiteSpace=wrap` on icons (labels wrap to icon width). Cut text nobody needs.
- Not built or prod-only parts: draw them faded (`opacity=35`) and label them "(prod)" or
  "(optional)". Never draw something as running when it is not.
